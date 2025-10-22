# Email Validation - HR

Email validation integration module for employees (hr.employee) in Odoo 16.0.

## Description

The `kw_email_validation_hr` module integrates email validation functionality with the Odoo HR module. It allows checking the correctness of employee work email addresses and visually displaying the validation status in the interface.

## Key Features

- Automatic validation of email addresses when creating/updating employee data
- Visual display of validation status with color coding:
  - Green - for valid addresses
  - Yellow - for addresses pending verification
  - Red - for invalid addresses
- Manual email verification through the action menu
- Bulk verification of multiple employees simultaneously
- Automatic validation of existing employees when installing the module

## Dependencies

- `hr` - Odoo HR base module
- `kw_email_validation` - base email validation module

## Installation

1. Install the base module `kw_email_validation`
2. Install the `kw_email_validation_hr` module
3. After installation, all existing employees with email addresses will be automatically added for verification

## Usage

### Automatic Validation

After installing the module, the system automatically checks email addresses when creating or updating employee data.

### Manual Validation

1. Open an employee card with an email address
2. Use the action menu to launch manual verification

### Bulk Validation

1. Select multiple employees in the list
2. Use the action menu to launch bulk verification

## Technical Details

The module extends the `hr.employee` model and adds corresponding fields and methods for email validation. It also updates the employee form view to display the validation status of the `work_email` field.

## License

LGPL-3

## Author

Kitworks Systems: https://kitworks.systems/
