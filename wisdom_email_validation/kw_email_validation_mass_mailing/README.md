# Email Validation - Mass Mailing

Email validation integration module for mailing contacts (mailing.contact) in Odoo 16.0.

## Description

The `kw_email_validation_mass_mailing` module integrates email validation functionality with the Odoo mass mailing module. It allows checking the correctness of mailing contact email addresses and visually displaying the validation status in the interface.

## Key Features

- Automatic validation of email addresses when creating/updating mailing contacts
- Visual display of validation status with color coding:
  - Green - for valid addresses
  - Yellow - for addresses pending verification
  - Red - for invalid addresses
- Manual email verification through the action menu
- Bulk verification of multiple contacts simultaneously
- Automatic validation of existing contacts when installing the module

## Dependencies

- `mass_mailing` - Odoo mass mailing module
- `kw_email_validation` - base email validation module

## Installation

1. Install the base module `kw_email_validation`
2. Install the `kw_email_validation_mass_mailing` module
3. After installation, all existing mailing contacts with email addresses will be automatically added for verification

## Usage

### Automatic Validation

After installing the module, the system automatically checks email addresses when creating or updating mailing contacts.

### Manual Validation

1. Open a mailing contact with an email address
2. Use the action menu to launch manual verification

### Bulk Validation

1. Select multiple mailing contacts in the list
2. Use the action menu to launch bulk verification

## Technical Details

The module extends the `mailing.contact` model and adds corresponding fields and methods for email validation. It also updates the form and list views of mailing contacts to display the validation status directly on the email field with appropriate color formatting.

## Benefits of Use

- Improved quality of the mailing contact database
- Reduced number of bounces when sending
- Enhanced sender reputation
- Increased email marketing effectiveness

## License

LGPL-3

## Author

Kitworks Systems: https://kitworks.systems/
