# Email Validation - HR Recruitment

Email validation integration module for job applicants (hr.applicant) in Odoo 16.0.

## Description

The `kw_email_validation_hr_recruitment` module integrates email validation functionality with the Odoo recruitment module. It allows checking the correctness of applicant email addresses and visually displaying the validation status in the interface.

## Key Features

- Automatic validation of email addresses when creating/updating applicant applications
- Visual display of validation status with color coding:
  - Green - for valid addresses
  - Yellow - for addresses pending verification
  - Red - for invalid addresses
- Manual email verification through the action menu
- Bulk verification of multiple applicants simultaneously
- Automatic validation of existing applications when installing the module

## Dependencies

- `hr_recruitment` - Odoo recruitment module
- `kw_email_validation` - base email validation module

## Installation

1. Install the base module `kw_email_validation`
2. Install the `kw_email_validation_hr_recruitment` module
3. After installation, all existing applicant applications with email addresses will be automatically added for verification

## Usage

### Automatic Validation

After installing the module, the system automatically checks email addresses when creating or updating applicant applications.

### Manual Validation

1. Open an applicant application with an email address
2. Use the action menu to launch manual verification

### Bulk Validation

1. Select multiple applicant applications in the list
2. Use the action menu to launch bulk verification

## Technical Details

The module extends the `hr.applicant` model and adds corresponding fields and methods for email validation. It also updates the form and list views of applicants to display the validation status directly on the email_from field with appropriate color formatting.

## Benefits of Use

- Improved communication quality with candidates
- Reduced errors when sending emails
- Ability to quickly identify incorrect email addresses
- Enhanced recruitment process

## License

LGPL-3

## Author

Kitworks Systems: https://kitworks.systems/
