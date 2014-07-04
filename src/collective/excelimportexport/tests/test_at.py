from collective.excelimportexport.tests import test_import


class TestArchetypesImport(test_import.TestDexterityImport):
    """
    Test processing spreadsheets for importing Archetypes content.
    """

    profile = None
    title_name = 'title'
    description_name = 'description'
    subjects_name = 'ICategorization.subject'
    location_name = 'ICategorization.location'
    title_type = description_type = text_type = str
