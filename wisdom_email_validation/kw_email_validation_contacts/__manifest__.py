{
    'name': 'Email Validation - Contacts',
    'summary': """
        This module integrates email validation with the Contacts module,
        allowing validation of partner email addresses.
    """,

    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/email-validation',

    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',

    'depends': [
        'contacts',
        'kw_email_validation',
    ],

    'external_dependencies': {'python': [], },

    'data': [
        'views/res_partner_views.xml',
    ],
    'demo': [
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': 'post_init_hook',

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

}
