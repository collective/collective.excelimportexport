from zope import interface
from zope import component
import zope.schema
from zope.schema import interfaces as schema_ifaces
from zope.container import interfaces as container_ifaces

from z3c.form import interfaces as form_ifaces
import z3c.form.widget
from z3c.form import widget

from Products.Five import metaclass

from Products.CMFCore import interfaces as cmf_ifaces
from Products.CMFCore.utils import getToolByName

from Products.Archetypes import BaseObject

from collective.excelimportexport import interfaces
from collective.excelimportexport import row


class IATField(interface.Interface):
    """
    A zope.schema field that wraps an Archetypes field.
    """


class IATWidget(interface.Interface):
    """
    A z3c.form widget that wraps an Archetypes widget.
    """


@interface.implementer_only(IATWidget)
class ATWidget(z3c.form.browser.widget.HTMLInputWidget, widget.Widget):
    """Input type archetypes widget implementation."""

    klass = u'archetypes-widget'
    css = u'archetypes'


@component.adapter(IATField, form_ifaces.IFormLayer)
@interface.implementer(form_ifaces.IFieldWidget)
def ATFieldWidget(field, request):
    """IFieldWidget factory for ATFields."""
    field_widget = widget.FieldWidget(field, ATWidget(request))
    return field_widget


@interface.implementer(schema_ifaces.IFromUnicode)
class ATField(zope.schema.Field):
    """
    Wrap an Archetypes field in a zope.schema field.
    """

    interface.implements(IATField)

    def __init__(self, at_field, instance, *args, **kw):
        if 'default' not in kw and hasattr(at_field, 'default'):
            kw['default'] = at_field.getDefault(instance)
        super(ATField, self).__init__(*args, **kw)
        self.instance = instance
        self.at_field = at_field

    def validate(self, value):
        """
        Use the Archetypes field to validate a value.
        """
        if not hasattr(self, 'at_field'):
            return
        errors = self.at_field.validate(value, self.instance)
        if errors:
            raise zope.schema.ValidationError(errors)

    def fromUnicode(self, str_):
        """
        Use the Archetypes field to process a string into a value.
        """
        mutator = self.at_field.getMutator(self.instance)
        if mutator is not None:
            mutator(str_)
        else:
            self.at_field.set(self.instance, str_)

        accessor = self.at_field.getEditAccessor(self.instance)
        if accessor is None:
            accessor = self.at_field.getAccessor(self.instance)
        if accessor is not None:
            value = accessor()
        else:
            value = self.at_field.get(self.instance)
        return value
        


class ATRowAddForm(row.RowAddForm):
    """
    Process a row as an AT add form.
    """
    interface.implements(interfaces.IRowAddForm)
    component.adapts(
        cmf_ifaces.IFolderish, interface.Interface,
        cmf_ifaces.ITypeInformation)

    # Override properties in favor of attributes set in self.update()
    description = None
    schema = None
    additionalSchemata = None

    def update(self):
        """
        Generate a zope schema from an AT schema.
        """
        types = getToolByName(self.context, 'portal_types')
        fti = types[self.portal_type]
        self.description = fti.Description()

        # Generate a class from which dummy AT instances can be made.
        # Cached on the types tool for per-portal dynamic schemata
        if not hasattr(types, '_v_at_z3c_form_classes'):
            types._v_at_z3c_form_classes = {}
        class_ = types._v_at_z3c_form_classes.get(self.portal_type)
        if class_ is None:
            factory = fti._queryFactoryMethod(self.context)
            class_ = factory.im_func.func_globals[factory.__name__[3:]]
            class_ = types._v_at_z3c_form_classes[
                self.portal_type] = metaclass.makeClass(
                    class_.__name__, (class_, ), dict(
                        __init__=BaseObject.BaseObject.__init__))
        self.instance = class_('instance').__of__(self.context)
        schemata = self.instance.Schemata()

        # Generate interfaces from the AT schemata
        self.schema = metaclass.makeClass(
            'I' + class_.__name__, (interface.Interface, ), dict(
                (name, ATField(schemata['default'][name], self.instance))
                for name in schemata['default'].keys()))
        self.additionalSchemata = (
            metaclass.makeClass(
                'I' + fieldset.capitalize(), (interface.Interface, ), dict(
                    (name, ATField(schemata[fieldset][name], self.instance))
                    for name in schemata[fieldset].keys()))
            for fieldset in schemata.keys() if fieldset != 'default')

        return super(ATRowAddForm, self).update()

    def updateActions(self):
        """
        Add AT defaults to the form.
        """
        # Do this in updateActions so we have the groups processed after
        # updateWidgets but before self.actions.execute in
        # z3c.form.group.GroupForm.update
        for group in (self, ) + self.groups:
            for name, widget in group.widgets.items():
                if (
                        not widget.field.required or
                        widget.name in self.request or
                        name == 'id'):
                    continue
                self.request.form[widget.name] = widget.field.default

        super(ATRowAddForm, self).updateActions()

    def createAndAdd(self, data):
        """
        Delegate to the portal_types tool for adding the content.
        """
        id_ = data.pop('id', '')
        self.instance.title = data.get('title', id_)
        if not id_:
            id_ = container_ifaces.INameChooser(self.context).chooseName(
                None, self.instance)
        new_id = self.context.invokeFactory(self.portal_type, id_, **data)
        return self.context[new_id]
