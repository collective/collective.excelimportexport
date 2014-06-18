import os
import unittest2 as unittest

from zope import interface

from z3c.form import interfaces as form_ifaces

from plone.testing import z2
from plone.app import testing as pa_testing

from Products.CMFCore.utils import getToolByName

from collective.excelimportexport import testing


class TestImport(unittest.TestCase):
    """
    Test processing spreadsheets for importing content.
    """

    layer = testing.COLLECTIVE_EXCELIMPORTEXPORT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.types = getToolByName(self.portal, 'portal_types')

    def assertDexterityRow(self):
        info = self.types['Document']
        schema = info.lookupSchema()

        import openpyxl
        workbook = openpyxl.load_workbook(os.path.join(
            os.path.dirname(__file__), 'import.xlsx'))
        sheet = workbook.worksheets[1]
        row = sheet.rows[1]

        from collective.excelimportexport.sheet import SheetForm
        request = self.portal.REQUEST.clone()
        interface.alsoProvides(request, form_ifaces.IFormLayer)
        sheet_form = SheetForm(self.portal, request, sheet)
        sheet_form.update()
        row_form = sheet_form.getRowForm(row)
        row_form.update()
        data, errors = row_form.extractData()
        self.assertFalse(errors, 'Validation errors in row')

        seen = []
        for attr in schema:
            seen.append(attr)
            self.assertIn(
                attr, data, 'Dexterity row data missing attribute')
            field = schema[attr]
            value = data[attr]
            self.assertIsInstance(
                value, field._type, 'Wrong imported field value type')

        unseen = set(seen) - set(data)
        self.assertFalse(unseen, 'Schema processing missed cells')

        return row_form

    def test_dexterity_extract_row_data(self):
        """
        Process a dexterity content spreadsheet row into a dict.
        """
        pa_testing.applyProfile(self.portal, 'plone.app.contenttypes:default')
        self.assertDexterityRow()

    def test_dexterity_extract_update_row_data(self):
        """
        Process a dexterity content row into a dict for existing content.
        """
        pa_testing.applyProfile(self.portal, 'plone.app.contenttypes:default')
        z2.login(self.layer['app']['acl_users'], pa_testing.SITE_OWNER_NAME)
        foo_doc = self.portal[
            self.portal.invokeFactory('Document', 'foo-document-title')]
        row_form = self.assertDexterityRow()
        self.assertEqual(
            row_form.context.getPhysicalPath(), foo_doc.getPhysicalPath(),
            'Wrong row edit form context')

    def test_dexterity_extract_replace_row_data(self):
        """
        Process a dexterity content row into a dict to replace content.
        """
        pa_testing.applyProfile(self.portal, 'plone.app.contenttypes:default')
        z2.login(self.layer['app']['acl_users'], pa_testing.SITE_OWNER_NAME)
        self.portal.invokeFactory('News Item', 'foo-document-title')
        self.assertDexterityRow()
        self.assertNotIn(
            'foo-document-title', self.portal,
            'Did not replace existing content of a different type')
