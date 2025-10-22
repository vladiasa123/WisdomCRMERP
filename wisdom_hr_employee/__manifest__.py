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
        'hr_skills',
        'hr_attendance_reason',
        'wisdom_employee_review',
        'event',
        'web'
    ],
    'data': [
        'wizard/wizard.xml',
        'security/security.xml',
        'views/res_user_views.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'wizard/import_volunteer_cv_wizard.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
