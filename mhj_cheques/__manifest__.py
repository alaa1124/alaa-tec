{
    'name': "Cheque Management",
    'summary': """ Full cheque life cycle Management. """,
    'version': '17.0.0.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'author': "Ultimate Code",
    'website': 'http://ultimatecode.co/',
    'depends': ['account','check_management'],
    'data': [
        'views/views.xml',
        # 'views/bank_stmt.xml',
        ],
    'application': True,
    'installable': True,
}
