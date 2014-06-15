from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectiveExcelImportExportLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.excelimportexport
        xmlconfig.file(
            'testing.zcml',
            collective.excelimportexport,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')


COLLECTIVE_EXCELIMPORTEXPORT_FIXTURE = CollectiveExcelImportExportLayer()
COLLECTIVE_EXCELIMPORTEXPORT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_EXCELIMPORTEXPORT_FIXTURE,),
    name="CollectiveExcelImportExportLayer:Integration"
)
COLLECTIVE_EXCELIMPORTEXPORT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_EXCELIMPORTEXPORT_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectiveExcelImportExportLayer:Functional"
)
