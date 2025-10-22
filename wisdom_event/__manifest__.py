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
        'event',
        'calendar'
    ],
    'data': [
        'views/event_form.xml',
        'views/raport_activitate.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}
