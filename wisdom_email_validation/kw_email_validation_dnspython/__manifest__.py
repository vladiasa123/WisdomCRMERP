{
    'name': 'Email Validation - DNS',
    'summary': """
        Module for email validation using DNS queries
        Uses the dnspython library to check domain MX records.
    """,

    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/email-validation',

    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',

    'depends': [
        'crm',
        'kw_email_validation',
    ],

    'external_dependencies': {
        'python': ['dnspython'],
    },

    'data': [
        'data/email_validator.xml',
    ],
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

}
