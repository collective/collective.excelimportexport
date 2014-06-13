======================================================================
Excel Import/Export
======================================================================
Import and export `CMF`_/`Plone`_ content using `excel`_ spreadsheets. 
----------------------------------------------------------------------

.. contents::

Introduction
============

This add-on provides support for importing and exporting Plone content to and
from spreadsheets such as those from `LibreOffice`_ or `Microsoft Excel`_.  It
can be useful for creating sample or initial content for use in QA, testing
and/or demoing in a format that is more accessible for non-technical users to
use.  In particular, errors that the user would encounter in import are
aggregated for all rows processed and written to the spreadcheet as highlighted
cells with error details in comments making it much easier for non-technical
users to iterate their own way to an importable spreadsheet.

It includes:

  * `GenericSetup`_ import and export steps
  * `transmogrifier`_ source and writer blueprints
  * browser views


Usage
=====

Spreadsheet Format
------------------

Import/Export sheets have ``portal_type`` and ``path`` columns.  Other columns
correspond to fields in the Dexterity or Archetypes schemata and as much as
possible cell data types and values conform to the field types.  Fields with
file content that shouldn't be put into cell values will be in files in a
directory whose path relative to the spreadsheet is the ``path`` cell value
with a ``.d`` suffix containing files with the same name as the field with the
appropriate extension.

On import, all sheets with ``portal_type`` and ``path`` columns will be
imported, other sheets will be ignored.  It's left up to the spreadsheet author
to make sure the columns correspond to arguments that the CMF content factory
can handle.  On export, each of the contexts passed as arguments will be
exported recursively into a separate sheet.

`GenericSetup`_
  For import, include a ``structure.xls.d`` directory in your GenericSetup
  profile containing spreadsheet files to be imported.  Columns other than
  ``portal_type`` and ``path`` will be passed to ``invokeFactory`` as keyword
  arguments.  For export, all site content will be exported int one sheet.

`transmogrifier`_ : TODO
  The source blueprint yields items for each row in the processed sheets from
  the directory specified in the section configuration.  The writer blueprint
  will write items to the spreadsheet specified in the section configuration
  for each item.

Browser views : TODO
  One browser view provides a form for uploading a spreadsheet from which to
  import content.  Other views support exporting content to a spread sheet from
  a single folder, the content listed in a collection, or the content listed in
  a search.


.. _`CMF`: http://old.zope.org/Products/CMF/index.html/
.. _`Plone`: http://plone.org
.. _`GenericSetup`: http://pythonhosted.org/Products.GenericSetup/
.. _`transmogrifier`: https://github.com/mjpieters/collective.transmogrifier

.. _`LibreOffice`: 
.. _`Microsoft Excel`: http://office.microsoft.com/en-us/excel/
.. _`excel`: `Microsoft Excel`_
