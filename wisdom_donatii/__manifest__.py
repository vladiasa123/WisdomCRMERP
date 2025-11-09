{
    'name': 'user creation wisdom',
    'summary': """
        Module for email validation using SMTP connection
        Checks mailbox existence by establishing SMTP connection.
    """,
    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/email-validation',

    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',

    'depends': [
        'base',
        'hr',
        'wisdom_hr_employee'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/donation_campaign_views.xml',
        'views/donation_view.xml',
        'wizard/donations_ai_report.xml',

    ],
    'installable': True,
    "application": True,    
    'auto_install': False,
}
