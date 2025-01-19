{
    'name': 'Analytic Costs Report',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Your Name',
    'depends': ['account'],
    'data': [
        'reports/analytic_cost_report.xml',  # Report Template
        'reports/analytic_cost_action.xml',  # Report Action
        'views/analytic_cost_report_template.xml',  # Report Template
    ],
    'installable': True,
    'application': False,
}
