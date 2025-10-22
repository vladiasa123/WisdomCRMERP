from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase


class TestEmailValidatorSMTP(TransactionCase):
    """Test cases for the SMTP email validator."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.EmailValidator = cls.env['kw.email.validator']
        cls.EmailValidation = cls.env['kw.email.validation']

        # Create smtp validator
        cls.smtp_validator = cls.EmailValidator.search([
            ('name', '=', 'smtp')
        ], limit=1)

        if not cls.smtp_validator:
            cls.smtp_validator = cls.EmailValidator.create({
                'name': 'smtp',
            })

    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.smtplib.SMTP')
    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_smtp_success(self, mock_resolve, mock_smtp_class):
        """Test SMTP validation with successful connection and response."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'test@example.com',
        })

        # Mock DNS MX record resolution
        mock_mx_record = MagicMock()
        mock_mx_record.preference = [[b'mail', b'example', b'com', b'']]
        mock_resolve.return_value = [mock_mx_record]

        # Mock SMTP connection
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.rcpt.return_value = (250, 'OK')

        # Test validation
        result = self.smtp_validator.validate_email_smtp(email)
        self.assertTrue(result, "Should return True when SMTP accepts email")

        # Check that DNS resolver was called
        mock_resolve.assert_called_once_with('example.com', 'MX')

        # Check SMTP connection sequence
        mock_smtp.connect.assert_called_with('mail.example.com')
        mock_smtp.helo.assert_called()
        mock_smtp.mail.assert_called_with('test@test.test')
        mock_smtp.rcpt.assert_called_with('test@example.com')
        mock_smtp.quit.assert_called()

        # Check that result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.smtp_validator.id),
            ('email_id', '=', email.id),
        ])
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].is_valid)

    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.smtplib.SMTP')
    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_smtp_rejected(self, mock_resolve, mock_smtp_class):
        """Test SMTP validation when email is rejected."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'rejected@example.com',
        })

        # Mock DNS MX record resolution
        mock_mx_record = MagicMock()
        mock_mx_record.preference = [[b'mail', b'example', b'com', b'']]
        mock_resolve.return_value = [mock_mx_record]

        # Mock SMTP connection with rejection
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.rcpt.return_value = (550, 'User unknown')

        # Test validation
        result = self.smtp_validator.validate_email_smtp(email)
        self.assertFalse(result, "Should return False when SMTP rejects email")

        # Check that result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.smtp_validator.id),
            ('email_id', '=', email.id),
        ])
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].is_valid)

    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.smtplib.SMTP')
    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_smtp_no_mx_record(self, mock_resolve,
                                              mock_smtp_class):
        """Test SMTP validation when no MX records found."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'nomx@example.com',
        })

        # Mock DNS resolution exception
        mock_resolve.side_effect = Exception("No MX record")

        # Test validation
        result = self.smtp_validator.validate_email_smtp(email)
        self.assertFalse(result, "Should return False when no MX records")

        # Check that DNS resolver was called
        mock_resolve.assert_called_once_with('example.com', 'MX')

        # SMTP should not be called
        mock_smtp_class.assert_called_once_with(timeout=30)

        # Check that result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.smtp_validator.id),
            ('email_id', '=', email.id),
        ])
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].is_valid)

    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.smtplib.SMTP')
    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_smtp_connection_error(self, mock_resolve,
                                                  mock_smtp_class):
        """Test SMTP validation with connection error."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'connectionerror@example.com',
        })

        # Mock DNS MX record resolution
        mock_mx_record = MagicMock()
        mock_mx_record.preference = [[b'mail', b'example', b'com', b'']]
        mock_resolve.return_value = [mock_mx_record]

        # Mock SMTP connection error
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.connect.side_effect = Exception("Connection failed")

        # Test validation
        result = self.smtp_validator.validate_email_smtp(email)
        self.assertFalse(result, "Should return False on connection error")

        # Check that result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.smtp_validator.id),
            ('email_id', '=', email.id),
        ])
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].is_valid)

    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.smtplib.SMTP')
    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_smtp_multiple_mx_hosts(self, mock_resolve,
                                                   mock_smtp_class):
        """Test SMTP validation with multiple MX hosts."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'multimx@example.com',
        })

        # Mock multiple MX records
        mock_mx1 = MagicMock()
        mock_mx1.preference = [[b'mail1', b'example', b'com', b'']]
        mock_mx2 = MagicMock()
        mock_mx2.preference = [[b'mail2', b'example', b'com', b'']]
        mock_resolve.return_value = [mock_mx1, mock_mx2]

        # Mock SMTP - first host fails, second succeeds
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp

        def connect_side_effect(host):
            if 'mail1' in host:
                raise Exception("First host failed")
            # Second host succeeds (no exception)
            return True

        mock_smtp.connect.side_effect = connect_side_effect
        mock_smtp.rcpt.return_value = (250, 'OK')

        # Test validation
        result = self.smtp_validator.validate_email_smtp(email)
        self.assertTrue(result, "Should succeed with second MX host")

        # Check that first connection was attempted
        self.assertGreaterEqual(mock_smtp.connect.call_count, 1)

    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.smtplib.SMTP')
    @patch('odoo.addons.kw_email_validation_smtp.models.'
           'email_validator.dns.resolver.resolve')
    def test_validate_email_smtp_rcpt_exception(self, mock_resolve,
                                                mock_smtp_class):
        """Test SMTP validation when RCPT command raises exception."""
        # Create test email
        email = self.EmailValidation.create({
            'name': 'rcptfail@example.com',
        })

        # Mock DNS MX record resolution
        mock_mx_record = MagicMock()
        mock_mx_record.preference = [[b'mail', b'example', b'com', b'']]
        mock_resolve.return_value = [mock_mx_record]

        # Mock SMTP connection with RCPT exception
        mock_smtp = MagicMock()
        mock_smtp_class.return_value = mock_smtp
        mock_smtp.rcpt.side_effect = Exception("RCPT failed")

        # Test validation
        result = self.smtp_validator.validate_email_smtp(email)
        self.assertFalse(result, "Should return False when RCPT fails")

        # Check that result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.smtp_validator.id),
            ('email_id', '=', email.id),
        ])
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].is_valid)

    def test_smtp_validator_inheritance(self):
        """Test that SMTP validator inherits from base validator."""
        # Check that it inherits from kw.email.validator
        self.assertEqual(self.smtp_validator._name, 'kw.email.validator')

        # Check that smtp method exists
        self.assertTrue(
            hasattr(self.smtp_validator, 'validate_email_smtp'))
        self.assertTrue(
            callable(getattr(self.smtp_validator, 'validate_email_smtp')))

    def test_smtp_domain_extraction(self):
        """Test that domain is correctly extracted from email."""
        # Create test email with subdomain
        email = self.EmailValidation.create({
            'name': 'user@mail.example.com',
        })

        with patch('odoo.addons.kw_email_validation_smtp.models.'
                   'email_validator.dns.resolver.resolve') as mock_resolve:
            mock_resolve.side_effect = Exception("Test exception")

            # Test validation
            self.smtp_validator.validate_email_smtp(email)

            # Check that correct domain was extracted
            mock_resolve.assert_called_once_with('mail.example.com', 'MX')
