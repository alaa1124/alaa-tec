# -*- coding: utf-8 -*-
{
    'name': "tender_crm",

    'summary': """
        create project form crm """,

    'description': """create project form crm
    """,

    'author': "My Company",


    'category': 'crm',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','tender'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
