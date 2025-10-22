{
    'name': 'Base Email Validation',
    'summary': """
        Base module for email validation functionality
        Provides core email validation functionality without external
        dependencies.
        Includes basic syntax checking and domain validation.
    """,

    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/email-validation',

    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',

    'depends': [
        'web',
    ],

    'external_dependencies': {'python': [], },

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/email_validator.xml',
        'data/ir_cron.xml',

        'views/menu_views.xml',
        'views/email_validation_views.xml',
        'views/email_validator_views.xml',
        'views/email_validation_rule_views.xml',
    ],
    'demo': [
        'demo/email_validation.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],
}
