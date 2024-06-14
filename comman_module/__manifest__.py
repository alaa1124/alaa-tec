# -*- coding: utf-8 -*-
{
    'name': "comman_module",

    'summary': """
                comman module between two modules tender,construction
""",

    'description': """
           comman module between two modules tender,construction
    """,

    'author': "My Company",

    'category': 'project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','project','product','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/item.xml',
        'views/related_job.xml',
        'views/products.xml',
        'views/job_cost.xml',
        'views/tender.xml',

    ],

}
