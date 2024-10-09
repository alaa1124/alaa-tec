# -*- coding: utf-8 -*-

{
    'name': "Journal Restrictions Global ",
    'summary': """Restrict users to certain journals""",
    'description': """Restrict users to certain journals.""",

    'license': 'AGPL-3',
    'category': 'account',
    'version': '17.0',
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
