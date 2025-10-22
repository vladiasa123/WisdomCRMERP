# Email Validation - Event

Email validation integration module for event registrations (event.registration) in Odoo 16.0.

## Description

The `kw_email_validation_event` module integrates email validation functionality with the Odoo events module. It allows checking the correctness of event participant email addresses and visually displaying the validation status in the interface.

## Key Features

- Automatic validation of email addresses when creating/updating event registrations
- Visual display of validation status with color coding:
  - Green - for valid addresses
  - Yellow - for addresses pending verification
  - Red - for invalid addresses
- Manual email verification through the action menu
- Bulk verification of multiple registrations simultaneously
- Automatic validation of existing registrations when installing the module

## Dependencies

- `event` - Odoo events module
- `kw_email_validation` - base email validation module

## Installation

1. Install the base module `kw_email_validation`
2. Install the `kw_email_validation_event` module
3. After installation, all existing registrations with email addresses will be automatically added for verification

## Usage

### Automatic Validation

After installing the module, the system automatically checks email addresses when creating or updating event registrations.

### Manual Validation

1. Open a registration with an email address
2. Use the action menu to launch manual verification

### Bulk Validation

1. Select multiple registrations in the list
2. Use the action menu to launch bulk verification

## Technical Details

The module extends the `event.registration` model and adds corresponding fields and methods for email validation. It also updates the form and list views of registrations to display the validation status directly on the email field with appropriate color formatting.

## License

LGPL-3

## Author

Kitworks Systems: https://kitworks.systems/
