import itertools
import operator

from zope import component

from z3c.form import form
from z3c.form import button

from Products.CMFCore.utils import getToolByName

from plone.app.layout.navigation import root

from collective.excelimportexport import interfaces


class SheetForm(form.Form):

    reserved = set(['portal_type', 'path'])
    
    def __init__(self, context, request, sheet):
        super(SheetForm, self).__init__(context, request)
        self.sheet = sheet

    def update(self):
        """
        Assemble forms for each row in the sheet.
        """
        self.rows = self.sheet.iter_rows()
        self.header = tuple(itertools.takewhile(
            operator.attrgetter('internal_value'), self.rows.next()))
        self.types = getToolByName(self.context, 'portal_types')

        super(SheetForm, self).update()

    @button.buttonAndHandler(u'Import', name='import')
    def handleImport(self, action):
        """
        Parse a rows into processed values and validation errors.
        """
        for row in self.rows:
            row_form = self.getRowForm(row)
            row_form()
            if getattr(row_form, 'errors', None):
                self.TODO()

    def getRowForm(self, row, action='save'):
        """
        Delegate each row to a separate form.
        """
        # Assemble a form submission from the row
        request = self.request.clone()
        for idx, header_cell in enumerate(self.header):
            key = header_cell.internal_value
            request.form[key] = row[idx].internal_value

        # Process the path before processing the form
        container_path, id_ = request.form.pop('path').rsplit('/', 1)
        nav = self.context
        if container_path.startswith('/'):
            # Start at the portal root
            container_path = container_path[1:]
            portal = getToolByName(
                self.context, 'portal_url').getPortalObject()
            nav = root.getNavigationRootObject(self.context, portal)
        container = nav.restrictedTraverse(container_path)

        portal_type = request.form.pop('portal_type')
        if portal_type not in self.types:
            raise ValueError('TODO Validation error on type')
        info = self.types[portal_type]

        # Lookup a form for the individual row
        if id_ in container:
            # Lookup the form based on existing content
            context = container[id_]
            if context.getPortalTypeName() != portal_type:
                # Replace existing content of a different type
                # TODO make configurable to raise a validation error
                container.manage_delObjects([id_])
                row_form = component.getMultiAdapter(
                    (container, request, info), interfaces.IRowAddForm)
            else:
                # Update existing content
                # TODO make configurable to raise a validation error
                row_form = component.getMultiAdapter(
                    (context, request), interfaces.IRowEditForm)
        else:
            # Lookup the form based on the content type
            row_form = component.getMultiAdapter(
                (container, request, info), interfaces.IRowAddForm)

        row_form.update()
        action = row_form.actions['save']
        row_form.request.form[action.name] = True

        return row_form
