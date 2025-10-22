# Email Validation Bundle

Metapackage for installing all email address validation modules in Odoo 16.0.

## Description

The `kw_email_validation_bundle` module is a metapackage that allows you to install all email address validation modules with a single click. This simplifies the installation process and ensures full functionality of the email address validation system across all Odoo modules.

## Included Modules

The metapackage includes the following modules:

1. **kw_email_validation** - base email address validation module
2. **kw_email_validation_contacts** - email validation for contacts (res.partner)
3. **kw_email_validation_crm** - email validation for CRM leads (crm.lead)
4. **kw_email_validation_hr** - email validation for employees (hr.employee)
5. **kw_email_validation_event** - email validation for event registrations (event.registration)
6. **kw_email_validation_mass_mailing** - email validation for mailing contacts (mailing.contact)
7. **kw_email_validation_hr_recruitment** - email validation for applicants (hr.applicant)
8. **kw_email_validation_smtp** - email validation when sending emails via SMTP
9. **kw_email_validation_dnspython** - enhanced validation using DNSPython
10. **kw_email_validation_web** - web interface for email validation

## Installation

1. Install the `kw_email_validation_bundle` module through the Odoo interface
2. All dependent modules will be installed automatically

## Configuration

After installing the metapackage, you need to configure validator parameters in the menu **Settings > Technical > Email Validation > Validators**.

## Benefits of Using the Metapackage

- Quick installation of all validation modules with a single click
- Guaranteed compatibility of all modules
- Automatic installation of all necessary dependencies
- Complete integration of email address validation across all Odoo modules

## License

LGPL-3

## Author

Kitworks Systems: https://kitworks.systems/
