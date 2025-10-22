# Email Validation Core Module

Core module for email address validation in Odoo 16.0.

## Description

The `kw_email_validation` module provides the core functionality for verifying the correctness of email addresses. It includes:

- The `kw.email.validation` model for storing validation results
- The `kw.email.validation.mixin` mixin for integration with other models
- Integration with external APIs for advanced validation
- Configuration of validation rules and priorities

## Key Features

- Email address syntax verification
- Domain and MX record verification
- Integration with external validation services
- Caching of validation results
- Configuration of validator priorities
- API connection testing

## Supported Validation Services

1. **NeverBounce** - high accuracy, speed, detailed information about results
2. **QuickEmailVerification** - high accuracy, speed, detailed information
3. **MillionVerifier** - medium accuracy, high speed, low price
4. **SendPulse** - integration with other SendPulse services
5. **ZeroBounce** - high accuracy, AI scoring, spam trap detection
6. **Clearout** - high accuracy, spam trap detection
7. **MailerCheck** - high accuracy, spam trap detection
8. **Mailgun** - high accuracy, integration with other Mailgun services

## Installation

1. Install the `kw_email_validation` module through the Odoo interface
2. Configure validator parameters in the menu **Settings > Technical > Email Validation > Validators**

## Usage in Other Modules

To use the validation functionality in other modules:

1. Add a dependency on `kw_email_validation` in your module's manifest
2. Inherit the `kw.email.validation.mixin` mixin in your model
3. Specify the email address field through the `_kw_email_validation_field` attribute
4. Add the `kw_email_validation_state` field to your model
5. Update views to display the validation status

Example:

```python
from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread', 'kw.email.validation.mixin']
    _kw_email_validation_field = 'email'
    
    email = fields.Char(string='Email')
    kw_email_validation_state = fields.Selection(
        related='kw_email_validation_id.state',
        string='Email Validation State',
        readonly=True,
    )
```

## License

LGPL-3

## Author

Kitworks Systems: https://kitworks.systems/
