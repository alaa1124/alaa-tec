# -*- coding: utf-8 -*-

{
    'name': "Journal Restrictions",
    'summary': """Restrict users to certain journals  convert from 10 : 13""",
    'description': """Restrict users to certain journals.""",
   
   
    'license': 'AGPL-3',
    'category': 'account',
    'version': '18.0',
    'depends': ['account'],
    'data': [
        'views/users.xml',
        'security/security.xml',
    ],
    "images": [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,

}
