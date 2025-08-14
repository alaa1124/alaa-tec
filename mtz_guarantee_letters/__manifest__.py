# -*- coding: utf-8 -*-
{
    'name': "UC Guarantee Letters",
    'summary': """Ultimate Code Guarantee letters""",
    'description': """ Guarantee letters""",
    'author': "Ultimate Code",
    'website': "http://www.ultimatecode.co",
    'version': "18.0",
    'category': 'Accounting',
    'depends': ['base_account_custom'],

    'license': 'AGPL-3',

    'data': [
        'security/ir.model.access.csv',
        'views/guarantee_letter.xml',
        'views/setting.xml',
        'views/guarantee_increase.xml',
        'views/guarantee_extension.xml',
        'views/guarantee_reduction.xml',
        'views/gurantee_completion.xml',
        'views/guarantee_send.xml',
        'views/guarantee_recieve.xml',
    ],

    'application': True,
    'installable': True,
}