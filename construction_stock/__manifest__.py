# -*- coding: utf-8 -*-
{
    'name': "construction_stock",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'category': 'Constructiom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'comman_module', 'tender'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/bank_statement.xml',
    ],

}
