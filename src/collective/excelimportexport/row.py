from zope import interface
from zope import component

from Products.CMFCore import interfaces as cmf_ifaces

from plone.dexterity import interfaces as dex_ifaces
from plone.dexterity.browser import add
from plone.dexterity.browser import edit

from collective.excelimportexport import interfaces


class RowForm(object):
    """
    Process a row as a form.
    """

    def updateFields(self):
        """
        Process the row as a form submission.
        """
        super(RowForm, self).updateFields()

        for group in [self] + self.groups:
            for name, field in group.fields.items():
                if field.field.__name__ in self.fields:
                    # Duplicate field names, can't guess to rename the row
                    continue
    
                # Add prefixes to schemata row field keys
                if field.field.__name__ in self.request.form:
                    self.request.form[name] = self.request.form.pop(
                        field.field.__name__)

    def updateWidgets(self):
        """
        Process the row as a form submission.
        """
        super(RowForm, self).updateWidgets()

        groups = []
        for groupClass in self.groups:
            group = groupClass(self.context, self.request, self)
            group.update()
            groups.append(group)
        self.groups = tuple(groups)
        
        for group in (self, ) + self.groups:
            for name, widget in group.widgets.items():

                # Add the form prefix to the row.
                if name in self.request.form:
                    self.request.form[
                        widget.name] = self.request.form.pop(name)
    
                # Add default values for required fields that have them to
                # avoid erroneous validation errors
                if (
                        widget.name not in self.request.form and
                        widget.field.required and
                        getattr(widget.field, 'default', None) is not None):
                    self.request.form[widget.name] = widget.terms.getTerm(
                        widget.field.default).token

    def updateActions(self):
        """
        Manually trigger the save action
        """
        super(RowForm, self).updateActions()

        save = self.actions['save']
        self.request.form[save.name] = True


class RowAddForm(RowForm, add.DefaultAddForm):
    """
    Process a row ass an add form.
    """
    interface.implements(interfaces.IRowAddForm)
    component.adapts(
        cmf_ifaces.IFolderish, interface.Interface, dex_ifaces.IDexterityFTI)


class RowEditForm(RowForm, edit.DefaultEditForm):
    """
    Process a row ass an edit form.
    """
    interface.implements(interfaces.IRowEditForm)
    component.adapts(
        dex_ifaces.IDexterityContent, interface.Interface)
