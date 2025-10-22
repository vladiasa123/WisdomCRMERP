from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase


class TestEmailValidatorDNSPython(TransactionCase):
    """Test cases for the DNS Python email validator."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.EmailValidator = cls.env['kw.email.validator']
        cls.EmailValidation = cls.env['kw.email.validation']

        # Create dnspython validator
        cls.dnspython_validator = cls.EmailValidator.search([
            ('name', '=', 'dnspython')
        ], limit=1)

        if not cls.dnspython_validator:
            cls.dnspython_validator = cls.EmailValidator.create({
                'name': 'dnspython',
            })

    @patch('odoo.addons.kw_email_validation_dnspython.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_dnspython_success(self, mock_resolve):
        """Test DNS Python validation with successful MX record lookup."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'test@example.com',
        })

        # Mock successful MX record resolution
        mock_mx_record = MagicMock()
        mock_resolve.return_value = [mock_mx_record]

        # Test validation
        result = self.dnspython_validator.validate_email_dnspython(email)
        self.assertTrue(result, "Should return True when MX records found")

        # Check that DNS resolver was called with correct parameters
        mock_resolve.assert_called_once_with('example.com', 'MX')

        # Check that result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.dnspython_validator.id),
            ('email_id', '=', email.id),
        ])
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].is_valid)

    @patch('odoo.addons.kw_email_validation_dnspython.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_dnspython_no_mx_record(self, mock_resolve):
        """Test DNS Python validation when no MX records found."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'test@nonexistent.com',
        })

        # Mock no MX records (empty list)
        mock_resolve.return_value = []

        # Test validation
        result = self.dnspython_validator.validate_email_dnspython(email)
        self.assertFalse(result, "Should return False when no MX records")

        # Check that DNS resolver was called
        mock_resolve.assert_called_once_with('nonexistent.com', 'MX')

        # Check that result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.dnspython_validator.id),
            ('email_id', '=', email.id),
        ])
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].is_valid)

    @patch('odoo.addons.kw_email_validation_dnspython.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_dnspython_dns_exception(self, mock_resolve):
        """Test DNS Python validation with DNS resolution exception."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'test@error.com',
        })

        # Mock DNS resolution exception
        mock_resolve.side_effect = Exception("DNS resolution failed")

        # Test validation
        result = self.dnspython_validator.validate_email_dnspython(email)
        self.assertFalse(result, "Should return False on DNS exception")

        # Check that DNS resolver was called
        mock_resolve.assert_called_once_with('error.com', 'MX')

        # Check that result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.dnspython_validator.id),
            ('email_id', '=', email.id),
        ])
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].is_valid)

    def test_validate_email_dnspython_domain_extraction(self):
        """Test that domain is correctly extracted from email."""
        # Create test email with subdomain
        email = self.EmailValidation.create({
            'name': 'user@mail.example.com',
        })

        with patch('odoo.addons.kw_email_validation_dnspython.models.'
                   'email_validator.dns.resolver.resolve') as mock_resolve:
            mock_resolve.return_value = [MagicMock()]

            # Test validation
            self.dnspython_validator.validate_email_dnspython(email)

            # Check that correct domain was extracted
            mock_resolve.assert_called_once_with('mail.example.com', 'MX')

    def test_validate_email_dnspython_multiple_at_symbols(self):
        """Test domain extraction with multiple @ symbols (edge case)."""
        # Create test email with multiple @ (though invalid format)
        email = self.EmailValidation.create({
            'name': 'user@name@example.com',
        })

        with patch('odoo.addons.kw_email_validation_dnspython.models.'
                   'email_validator.dns.resolver.resolve') as mock_resolve:
            mock_resolve.return_value = [MagicMock()]

            # Test validation
            self.dnspython_validator.validate_email_dnspython(email)

            # Should take the last part after splitting by @
            mock_resolve.assert_called_once_with('example.com', 'MX')

    def test_dnspython_validator_inheritance(self):
        """Test that DNS Python validator inherits from base validator."""
        # Check that it inherits from kw.email.validator
        self.assertEqual(self.dnspython_validator._name, 'kw.email.validator')

        # Check that dnspython method exists
        self.assertTrue(
            hasattr(self.dnspython_validator, 'validate_email_dnspython'))
        self.assertTrue(
            callable(getattr(self.dnspython_validator,
                             'validate_email_dnspython')))

    def test_dnspython_use_fname_decorator(self):
        """Test that dnspython validator works with use_fname decorator."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'decorator@example.com',
        })

        with patch('odoo.addons.kw_email_validation_dnspython.models.'
                   'email_validator.dns.resolver.resolve') as mock_resolve:
            mock_resolve.return_value = [MagicMock()]

            # Test validation using general validate_email method
            # (should call validate_email_dnspython via decorator)
            result = self.dnspython_validator.validate_email(email)
            self.assertTrue(result)

            # Check that DNS resolver was called
            mock_resolve.assert_called_once_with('example.com', 'MX')

    @patch('odoo.addons.kw_email_validation_dnspython.models.'
           'email_validator.dns.resolver.resolve')
    def test_dnspython_store_result_called(self, mock_resolve):
        """Test that store_result is called with correct parameters."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'store@example.com',
        })

        # Mock successful resolution
        mock_resolve.return_value = [MagicMock()]

        # Test validation
        self.dnspython_validator.validate_email_dnspython(email)

        # Check that validation result was stored
        result = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.dnspython_validator.id),
            ('email_id', '=', email.id),
        ], limit=1)

        self.assertTrue(result, "Validation result should be stored")
        self.assertEqual(result.name, 'store@example.com')
        self.assertEqual(result.validator_id, self.dnspython_validator)
        self.assertEqual(result.email_id, email)
        self.assertTrue(result.is_valid)
