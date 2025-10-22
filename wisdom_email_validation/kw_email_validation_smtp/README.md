# Email Validation - SMTP

Email address validation module for mail sending via SMTP in Odoo 16.0.

## Description

The `kw_email_validation_smtp` module integrates email address validation functionality with Odoo's mail sending system. It allows checking the correctness of email addresses before sending emails, which reduces the number of errors and improves communication efficiency.

## Key Features

- Automatic validation of email addresses before sending emails
- Prevention of sending emails to invalid addresses
- Warnings about potential delivery problems
- Improvement of sender reputation

## Dependencies

- `mail` - Odoo base mail module
- `kw_email_validation` - base email validation module

## Installation

1. Install the base module `kw_email_validation`
2. Install the `kw_email_validation_smtp` module

## Usage

After installing the module, the system will automatically check email addresses before sending emails. No additional configuration is required.

### Behavior when detecting invalid addresses

The module can operate in one of two modes (depending on settings):

1. **Warning mode** - shows warnings about invalid addresses but allows sending
2. **Blocking mode** - blocks sending emails to invalid addresses

## Technical Details

The module extends the standard email sending process in Odoo by adding an email address validation step before sending. It uses existing validation results or initiates a new check if results are missing or outdated.

## Benefits

- Reduction of errors when sending emails
- Improvement of sender reputation
- Reduction of bounces and rejections
- Resource savings on processing undelivered emails

## License

LGPL-3

## Author

Kitworks Systems: https://kitworks.systems/
