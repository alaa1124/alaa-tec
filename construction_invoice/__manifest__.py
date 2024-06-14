# -*- coding: utf-8 -*-
{
    'name': "construction_invoice",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "MOHAMED ABDELRHNAB",

    'category': 'Construction',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contract','engineer_techincal','account','account_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/engineer_tem.xml',
        'views/payment.xml',
        'views/menu.xml',
        'views/journal item.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
