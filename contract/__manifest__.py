# -*- coding: utf-8 -*-
{
    'name': "contract",

    'summary': """
       contract""",

    'description': """
       create contracct 
    """,

    'author': "MOHAMED ABDELRHMAN -00201128218762",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','comman_module'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/contract.xml',
        'views/subcontract.xml',
        'views/actions.xml',
        'views/menus.xml',

        'views/contract_config.xml',
        'views/deduction_contract.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
} 
