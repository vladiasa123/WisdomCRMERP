{
    'name': 'Beneficiari Management',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',
    'category': 'CRM',
    'summary': 'Manage beneficiaries in a standalone CRM-style module',
    'description': """
        A custom CRM-like module for managing beneficiaries,
        completely independent from Odoo's built-in CRM.
    """,
    'author': 'Your Name',
    'depends': ['base', 'wisdom_hr_employee'],
    'data': [
        'security/ir.model.access.csv',
        'views/beneficiari_views.xml',
        'views/courses_views.xml',
        'views/beneficiar_curs_views.xml',
        'views/instrument_views.xml',
        'views/activitate.xml',
        'views/fisa_servicii.xml'
    ],
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
