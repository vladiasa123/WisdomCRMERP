{
    'name': 'Email Validation',
    'summary': """
        Advanced email validation system for Odoo | Email verification
        Comprehensive solution for email validation, including syntax checking,
        domain verification, SMTP validation, DNS validation, regex validation,
        and integration with external validation services: NeverBounce,
        QuickEmailVerification, MillionVerifier, Clearout, MailerCheck,
        Mailgun, SendPulse, ZeroBounce. Email validation, verification service,
        email checker, address checker, list cleaning, bounce prevention,
        bulk validation, email deliverability.
    """,

    'author': 'Kitworks Systems',
    'website': 'https://github.com/kitworks-systems/email-validation',

    'category': 'Customizations',
    'license': 'LGPL-3',
    'version': '18.0.1.0.0',

    'depends': [
        'kw_email_validation',
        'kw_email_validation_contacts',
        'kw_email_validation_crm',
        'kw_email_validation_dnspython',
        'kw_email_validation_event',
        'kw_email_validation_hr',
        'kw_email_validation_hr_recruitment',
        'kw_email_validation_mass_mailing',
        'kw_email_validation_smtp',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

}
