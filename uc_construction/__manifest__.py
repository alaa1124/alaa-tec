# -*- coding: utf-8 -*-
{
    'name': "Construction",

    'summary': """
        Ultimate Code Construction Module""",

    'description': """
        the main purpose of the UC Construction is to build a conberhansive module to administrate the Construction field   """,

    'author': "Ultimate Code",
    'website': "http://www.ultimatecode.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services',
    'version': '0.1',
    'application': 'True',
    'installable': 'True',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'account', 'utm', 'stock'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'wizards/edit_imported_material.xml',
        'views/indirect_sites_tec.xml',
        'views/indirect_guard.xml',
        'views/indirect_acc.xml',
        'views/indirect_others.xml',
        'views/indirect_sites_cleaning.xml',
        'views/indirect_travel.xml',
        'views/indirect_cars.xml',
        'views/indirect_taxes.xml',
        'views/indirect_stamps.xml',
        'views/uc_stamps.xml',
        'views/tender_item_material.xml',
        'views/uc_tender_items.xml',
        'views/uc_tender.xml',
        'views/project.xml',
        'views/product.xml',
        'views/menu.xml',
        'data/data.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #
    #         'uc_construction/static/src/js/header.js',
    #     ],
    #
    # },

    'license': 'AGPL-3',

}
