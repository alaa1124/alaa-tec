{
    'name': 'Stock Picking Backdate',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'author': "10 Orbits",
    'website': "https://www.10orbits.com",
    'summary': 'This module allows you to entry the stock accounting details in backdate.',
    'depends': [
        'stock', 'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/change_to_backdate_wiz.xml',
        'wizard/inherit_stock_view_picking_form.xml',
        'views/stock_picking_backdate_action.xml'
    ],
    'images': ['static/description/Banner.png'],
    'application': False,
    'installable': True,
    'auto_install': False,
}
