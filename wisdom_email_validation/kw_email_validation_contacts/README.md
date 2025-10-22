# Email Validation - Contacts

Email validation integration module for contacts (res.partner) in Odoo 16.0.

## Description

The `kw_email_validation_contacts` module integrates email validation functionality with the Odoo contacts module. It allows checking the correctness of partner email addresses and visually displaying the validation status in the interface.

## Key Features

- Automatic validation of email addresses when creating/updating contacts
- Visual display of validation status with color coding:
  - Green - for valid addresses
  - Yellow - for addresses pending verification
  - Red - for invalid addresses
- Manual email verification through the action menu
- Bulk verification of multiple contacts simultaneously
- Automatic validation of existing contacts when installing the module

## Dependencies

- `contacts` - Odoo contacts module
- `kw_email_validation` - base email validation module

## Installation

1. Install the base module `kw_email_validation`
2. Install the `kw_email_validation_contacts` module
3. After installation, all existing contacts with email addresses will be automatically added for verification

## Usage

### Automatic Validation

After installing the module, the system automatically checks email addresses when creating or updating contacts.

### Manual Validation

1. Open a contact with an email address
2. Use the action menu to launch manual verification

### Bulk Validation

1. Select multiple contacts in the list
2. Use the action menu to launch bulk verification

## Technical Details

The module extends the `res.partner` model and adds corresponding fields and methods for email validation. It also updates the form and list views of contacts to display the validation status.

## License

LGPL-3

## Автор

Kitworks Systems: https://kitworks.systems/
