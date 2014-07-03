import os
import unittest2 as unittest

from zope import interface
from zope.publisher import browser

from ZPublisher import HTTPRequest

from plone.testing import z2
from plone.app import testing as pa_testing
from plone.app.z3cform import interfaces as z3cform_ifaces

from Products.CMFCore.utils import getToolByName

from collective.excelimportexport import testing


class TestDexterityImport(unittest.TestCase):
    """
    Test processing spreadsheets for importing content.
    """

    layer = testing.COLLECTIVE_EXCELIMPORTEXPORT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.types = getToolByName(self.portal, 'portal_types')
        pa_testing.applyProfile(self.portal, 'plone.app.contenttypes:default')

        import openpyxl
        self.workbook_path = os.path.join(
            os.path.dirname(__file__), 'import.xlsx')
        self.workbook = openpyxl.load_workbook(
            self.workbook_path, use_iterators=True)
        self.sheet = self.workbook.worksheets[1]
        self.rows = self.sheet.iter_rows()
        self.header = self.rows.next()
        self.row = self.rows.next()

    def getRowForm(self):
        from collective.excelimportexport.sheet import WorkbookForm
        request = self.portal.REQUEST.clone()
        interface.alsoProvides(request, z3cform_ifaces.IPloneFormLayer)
        book_form = WorkbookForm(self.portal, request)
        book_form.update()
        book_form.updateSheet(self.sheet)
        return book_form.getRowForm(self.row)
        
    def assertDexterityRow(self):
        info = self.types['Document']
        schema = info.lookupSchema()

        row_form = self.getRowForm()
        z2.login(self.layer['app']['acl_users'], pa_testing.SITE_OWNER_NAME)
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
        self.assertDexterityRow()

    def test_dexterity_extract_update_row_data(self):
        """
        Process a dexterity content row into a dict for existing content.
        """
        z2.login(self.layer['app']['acl_users'], pa_testing.SITE_OWNER_NAME)
        foo_doc = self.portal[
            self.portal.invokeFactory('Document', 'foo-document-title')]
        row_form = self.assertDexterityRow()
        self.skipTest('TODO add id column support for replacing content')
        self.assertEqual(
            row_form.context.getPhysicalPath(), foo_doc.getPhysicalPath(),
            'Wrong row edit form context')

    def test_dexterity_extract_replace_row_data(self):
        """
        Process a dexterity content row into a dict to replace content.
        """
        z2.login(self.layer['app']['acl_users'], pa_testing.SITE_OWNER_NAME)
        self.portal.invokeFactory('News Item', 'foo-document-title')
        self.assertDexterityRow()
        self.assertIn(
            'foo-document-title', self.portal,
            'Only removed existing content, should be replaced')
        foo_doc = self.portal['foo-document-title']
        self.skipTest('TODO add id column support for replacing content')
        self.assertEqual(
            foo_doc.getPortalTypeName(), self.row[0].internal_value,
            'Wrong content type')

    def test_dexterity_add(self):
        """
        Importing a row can add dexterity content.
        """
        self.assertNotIn(
            'foo-document-title', self.portal,
            'Content exists before importing')
        row_form = self.getRowForm()
        z2.login(self.layer['app']['acl_users'], pa_testing.SITE_OWNER_NAME)
        row_form()
        self.assertIn(
            'foo-document-title', self.portal,
            'Content not created from import')
        foo_doc = self.portal['foo-document-title']
        self.assertEqual(
            foo_doc.getPortalTypeName(), self.row[0].internal_value,
            'Wrong content type')
        self.assertEqual(
            foo_doc.Title(), self.row[1].internal_value, 'Wrong title value')
        self.assertEqual(
            foo_doc.Description(),  self.row[2].internal_value,
            'Wrong title value')
        self.assertEqual(
            foo_doc.text.raw,  self.row[3].internal_value,
            'Wrong text value')

    def test_sheet_import(self):
        """
        Importing a whole sheet imports multiple content objects.
        """
        self.assertNotIn(
            'foo-document-title', self.portal,
            'Content exists before importing')
        self.assertNotIn(
            'bar-news-item-title', self.portal,
            'Content exists before importing')

        from collective.excelimportexport.sheet import WorkbookForm
        request = self.portal.REQUEST.clone()
        interface.alsoProvides(request, z3cform_ifaces.IPloneFormLayer)
        workbook_form = WorkbookForm(self.portal, request)
        workbook_form.update()

        # Stub out a file upload submittions
        widget = workbook_form.widgets['workbook']
        storage = browser.ZopeFieldStorage(environ={})
        storage.file = open(self.workbook_path)
        storage.filename = storage.file.name
        workbook_form.request.form[
            widget.name] = HTTPRequest.FileUpload(storage)

        action = workbook_form.actions['import']
        workbook_form.request.form[action.name] = True

        z2.login(self.layer['app']['acl_users'], pa_testing.SITE_OWNER_NAME)
        workbook_form()

        self.assertIn(
            'foo-document-title', self.portal,
            'Content not created from import')
        self.assertIn(
            'bar-news-item-title', self.portal,
            'Content not created from import')

    def test_workbook_import(self):
        """
        Importing a whole workbook imports multiple sheets.
        """
        self.assertNotIn(
            'foo-document-title', self.portal,
            'Content exists before importing')
        self.assertNotIn(
            'bar-news-item-title', self.portal,
            'Content exists before importing')
        self.assertNotIn(
            'corge-document-title', self.portal,
            'Content exists before importing')

        from collective.excelimportexport.sheet import WorkbookForm
        request = self.portal.REQUEST.clone()
        interface.alsoProvides(request, z3cform_ifaces.IPloneFormLayer)
        workbook_form = WorkbookForm(self.portal, request)
        workbook_form.update()

        # Stub out a file upload submittions
        widget = workbook_form.widgets['workbook']
        storage = browser.ZopeFieldStorage(environ={})
        storage.file = open(self.workbook_path)
        storage.filename = storage.file.name
        workbook_form.request.form[
            widget.name] = HTTPRequest.FileUpload(storage)
        
        action = workbook_form.actions['import']
        workbook_form.request.form[action.name] = True
        z2.login(self.layer['app']['acl_users'], pa_testing.SITE_OWNER_NAME)
        workbook_form()

        self.assertIn(
            'foo-document-title', self.portal,
            'Content not created from import')
        self.assertIn(
            'bar-news-item-title', self.portal,
            'Content not created from import')
        self.assertIn(
            'garply-folder-title', self.portal,
            'Content not created from import')
        
