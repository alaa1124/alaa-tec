# -*- coding: utf-8 -*-
{
    'name': "cheques Management",

    'summary': """
        Checque managment Cycle""",

    'description': """
        Long description of module's purpose
    """,
    'author': "Emad Adeeb",
    'website': "http://www.EmadAdeep.co",
    'category': 'account',
    'version': '18.0',

    # any module necessary for this one to work correctly
    'depends': ['base_account_custom', 'account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
         'security/group_user.xml',

        'views/cheque_recieve_view.xml',
        'views/views.xml',
        'views/config.xml',
        'views/payment_actions.xml',
        'views/cheque_send_view.xml',
        'views/cheque_document.xml',
        'reports/payment_voucher.xml',
        'reports/receipt_voucher.xml',
        'reports/invoices.xml',

    ],

    'license': 'AGPL-3',

}