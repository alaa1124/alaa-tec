# -*- coding: utf-8 -*-
{
    'name': "tender",

    'summary': """
    Tender Module
    """,

    'description': """
        Tender Module
    """,

    'author': "My Company",
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project','comman_module'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/actions.xml',
        'views/menus.xml',
        'views/views.xml',
        'views/config.xml',
        'views/indirect_cost.xml',
        'views/top_sheet.xml',
        'views/sale_order.xml',
        'views/project.xml',
        'views/templates.xml',
    ],

}
