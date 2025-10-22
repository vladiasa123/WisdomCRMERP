# Email Validation - DNSPython

Advanced email address validation module using DNSPython in Odoo 16.0.

## Description

The `kw_email_validation_dnspython` module extends the base email validation module using the DNSPython library. It allows for more detailed domain and MX record verification to improve validation accuracy.

## Key Features

- Enhanced DNS record verification for domains
- Detailed MX record checking
- Mail server availability verification
- Detection of potentially invalid domains

## Dependencies

- `kw_email_validation` - base email validation module

### External Python Dependencies

- `dnspython` - Python DNS library

## Installation

1. Install the base module `kw_email_validation`
2. Install the `dnspython` library:
   ```bash
   pip install dnspython
   ```
3. Install the `kw_email_validation_dnspython` module

## Usage

After installing the module, the system will automatically use enhanced DNS verification when validating email addresses. No additional configuration is required.

## Technical Details

The module adds a new validator `dnspython`, which performs the following checks:

1. Domain existence verification
2. MX record presence verification
3. Mail server availability verification

## Benefits

- Improved validation accuracy without using external APIs
- No limitations on the number of verifications
- Fast verification without delays for requests to external services

## License

LGPL-3

## Author

Kitworks Systems: https://kitworks.systems/
