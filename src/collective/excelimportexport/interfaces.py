from zope import interface


class IRowAddForm(interface.Interface):
    """
    A form that adds content from data in a spreadsheet row.
    """


class IRowEditForm(interface.Interface):
    """
    A form that updates content from data in a spreadsheet row.
    """
