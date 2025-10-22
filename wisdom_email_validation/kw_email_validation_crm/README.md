# Email Validation - CRM

Email validation integration module for CRM leads (crm.lead) in Odoo 16.0.

## Description

The `kw_email_validation_crm` module integrates email validation functionality with the Odoo CRM module. It allows checking the correctness of lead email addresses and visually displaying the validation status in the interface.

## Key Features

- Automatic validation of email addresses when creating/updating leads
- Visual display of validation status with color coding:
  - Green - for valid addresses
  - Yellow - for addresses pending verification
  - Red - for invalid addresses
- Manual email verification through the action menu
- Bulk verification of multiple leads simultaneously
- Automatic validation of existing leads when installing the module

## Dependencies

- `crm` - Odoo CRM module
- `kw_email_validation` - base email validation module

## Installation

1. Install the base module `kw_email_validation`
2. Install the `kw_email_validation_crm` module
3. After installation, all existing leads with email addresses will be automatically added for verification

## Usage

### Automatic Validation

After installing the module, the system automatically checks email addresses when creating or updating leads.

### Manual Validation

1. Open a lead with an email address
2. Use the action menu to launch manual verification

### Bulk Validation

1. Select multiple leads in the list
2. Use the action menu to launch bulk verification

## Technical Details

The module extends the `crm.lead` model and adds corresponding fields and methods for email validation. It also updates the form and list views of leads to display the validation status.

## License

LGPL-3

## Автор

Kitworks Systems: https://kitworks.systems/
