from unittest.mock import patch

from odoo import exceptions
from odoo.tests.common import TransactionCase


class TestEmailValidator(TransactionCase):
    """Test cases for the kw.email.validator model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.EmailValidator = cls.env['kw.email.validator']
        cls.EmailValidation = cls.env['kw.email.validation']

        # Use existing validators from data files
        cls.regexp_validator = cls.EmailValidator.search(
            [('name', '=', 'regexp')], limit=1)
        cls.neverbounce_validator = cls.EmailValidator.search(
            [('name', '=', 'neverbounce')], limit=1)
        cls.zerobounce_validator = cls.EmailValidator.search(
            [('name', '=', 'zerobounce')], limit=1)
        cls.sendpulse_validator = cls.EmailValidator.search(
            [('name', '=', 'sendpulse')], limit=1)

        # Add API keys for testing
        if cls.neverbounce_validator:
            cls.neverbounce_validator.api_key = 'test_neverbounce_key'
        if cls.zerobounce_validator:
            cls.zerobounce_validator.api_key = 'test_zerobounce_key'
        if cls.sendpulse_validator:
            cls.sendpulse_validator.api_key = 'test_user_id:test_secret'

    def test_validate_email_regexp(self):
        """Test regexp validation - both direct method and via decorator."""
        # Create test emails
        valid_email = self.EmailValidation.create({
            'name': 'valid@example.com',
        })
        invalid_email = self.EmailValidation.create({
            'name': 'invalid@example',
        })

        # Test 1: Direct call to validate_email_regexp method
        result_valid_direct = (
            self.regexp_validator.validate_email_regexp(valid_email))
        self.assertTrue(result_valid_direct,
                        "Valid email should pass direct regexp "
                        "validation")

        result_invalid_direct = (
            self.regexp_validator.validate_email_regexp(invalid_email))
        self.assertFalse(result_invalid_direct,
                         "Invalid email should fail direct regexp "
                         "validation")

        # Test 2: Call via validate_email method (uses decorator)
        valid_email2 = self.EmailValidation.create({
            'name': 'valid2@example.com',
        })
        invalid_email2 = self.EmailValidation.create({
            'name': 'invalid2@example',
        })

        result_valid_decorator = (
            self.regexp_validator.validate_email(valid_email2))
        self.assertTrue(result_valid_decorator,
                        "Valid email should pass decorator regexp "
                        "validation")

        result_invalid_decorator = (
            self.regexp_validator.validate_email(invalid_email2))
        self.assertFalse(result_invalid_decorator,
                         "Invalid email should fail decorator "
                         "regexp validation")

        # Check that results were stored for all validations
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.regexp_validator.id),
        ])
        self.assertEqual(len(results), 4,
                         "Should store four validation results")

    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.get')
    def test_validate_email_neverbounce_api(self, mock_get):
        """Test NeverBounce API validation using real validator."""
        if not self.neverbounce_validator:
            self.skipTest("NeverBounce validator not found in data files")

        # Create a test email
        email = self.EmailValidation.create({
            'name': 'api@example.com',
        })

        # Mock successful API response for NeverBounce
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'status': 'success',
            'result': 'valid'
        }

        # Test validation using real neverbounce validator
        result = self.neverbounce_validator.validate_email(email)
        self.assertTrue(
            result,
            "NeverBounce validation should succeed with valid response")

        # Check API call parameters - URL має бути з підставленими значеннями
        mock_get.assert_called_with(
            ('https://api.neverbounce.com/v4/single/check?'
             'key=test_neverbounce_key&email=api@example.com'),
            params={}, headers={}, auth=None, timeout=30
        )

        # Mock failed API response
        mock_get.return_value.json.return_value = {
            'status': 'success',
            'result': 'invalid'
        }

        # Test validation
        result = self.neverbounce_validator.validate_email(email)
        self.assertFalse(
            result,
            "NeverBounce validation should fail with invalid response")

    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.get')
    def test_validate_email_zerobounce_api_error(self, mock_get):
        """Test ZeroBounce API validation with errors."""
        if not self.zerobounce_validator:
            self.skipTest("ZeroBounce validator not found in data files")

        # Create a test email
        email = self.EmailValidation.create({
            'name': 'api_error@example.com',
        })

        # Mock API error
        mock_get.side_effect = Exception("API Error")

        # Test validation using real zerobounce validator
        result = self.zerobounce_validator.validate_email(email)
        self.assertFalse(result, "ZeroBounce validation should "
                                 "fail on exception")

        # Check that error result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.zerobounce_validator.id),
            ('email_id', '=', email.id),
            ('is_valid', '=', False),
        ])
        self.assertEqual(len(results), 1,
                         "Should store error validation result")

    def test_api_key_required(self):
        """Test that API key is required for API validators."""
        if not self.neverbounce_validator:
            self.skipTest("NeverBounce validator not found in data files")

        # Remove API key temporarily
        original_key = self.neverbounce_validator.api_key
        self.neverbounce_validator.api_key = False

        try:
            # Create a test email
            email = self.EmailValidation.create({
                'name': 'no_key@example.com',
            })

            # Test validation - should raise ValidationError
            with self.assertRaises(exceptions.ValidationError):
                self.neverbounce_validator.validate_email(email)
        finally:
            # Restore API key
            self.neverbounce_validator.api_key = original_key

    def test_api_key_visibility(self):
        """Test API key visibility toggle."""
        if not self.neverbounce_validator:
            self.skipTest("NeverBounce validator not found in data files")

        # Initially API key should not be visible
        self.assertFalse(self.neverbounce_validator.is_api_key_visible)

        # Show API key
        self.neverbounce_validator.show_api_key()
        self.assertTrue(self.neverbounce_validator.is_api_key_visible)

        # Hide API key
        self.neverbounce_validator.hide_api_key()
        self.assertFalse(self.neverbounce_validator.is_api_key_visible)

    def test_direct_api_method_call(self):
        """Test direct API method call using
        _validate_email_url_api_generic."""
        if not self.neverbounce_validator:
            self.skipTest("NeverBounce validator not found in data files")

        # Create a test email
        email = self.EmailValidation.create({
            'name': 'direct@example.com',
        })

        # Test direct call to generic method
        with patch(
                'odoo.addons.kw_email_validation.models.email_validator.'
                'requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'result': 'valid'}

            result = self.neverbounce_validator.\
                _validate_email_url_api_generic(email)
            self.assertTrue(
                result,
                "Direct generic API call should succeed with valid response")

    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.get')
    def test_test_connection(self, mock_get):
        """Test the test_connection method using real validator."""
        if not self.neverbounce_validator:
            self.skipTest("NeverBounce validator not found in data files")

        # Mock successful API response for NeverBounce
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'status': 'success',
            'result': 'valid'
        }

        # Test connection - має використати validate_email_neverbounce метод
        result = self.neverbounce_validator.test_connection()
        self.assertTrue(
            result.get('success', False),
            f"Connection test should succeed with valid response. "
            f"Got: {result}")

        # Test connection without API key
        validator = self.EmailValidator.create({
            'name': 'test_no_key',
            'url': 'https://api.example.com/validate',
        })

        result = validator.test_connection()
        self.assertFalse(result.get('success', True),
                         "Connection test should fail without API key")

    def test_use_fname_decorator(self):
        """Test the use_fname decorator using real validators."""
        # Test case 1: Validator with existing custom method (regexp)
        if not self.regexp_validator:
            self.skipTest("Regexp validator not found in data files")

        email1 = self.EmailValidation.create({
            'name': 'valid@example.com',
        })

        # Test validation - should use validate_email_regexp method
        result1 = self.regexp_validator.validate_email(email1)
        self.assertTrue(
            result1,
            "Regexp validation method should be used for valid email")

        # Test case 2: Validator with existing custom method (neverbounce)
        if self.neverbounce_validator:
            email2 = self.EmailValidation.create({
                'name': 'test@example.com',
            })

            # Mock API response for this test
            with patch(
                    'odoo.addons.kw_email_validation.models.'
                    'email_validator.requests.get') as mock_get:
                mock_get.return_value.status_code = 200
                mock_get.return_value.json.return_value = {
                    'status': 'success',
                    'result': 'valid'
                }

                # Test validation - should use validate_email_neverbounce
                # method
                result2 = self.neverbounce_validator.validate_email(email2)
                self.assertTrue(result2,
                                "NeverBounce validation method should be used")

        # Test case 3: Validator without custom method (should use base)
        validator_without_custom = self.EmailValidator.create({
            'name': 'no_custom_method',
        })

        email3 = self.EmailValidation.create({
            'name': 'test3@example.com',
        })

        # Test validation - should use base validate_email method
        # (returns True)
        result3 = validator_without_custom.validate_email(email3)
        self.assertTrue(
            result3,
            "Base validation method should be used when custom method "
            "not found")

    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.post')
    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.get')
    def test_validate_email_sendpulse_success(self, mock_get, mock_post):
        """Test SendPulse API validation with successful response."""
        if not self.sendpulse_validator:
            self.skipTest("SendPulse validator not found in data files")

        # Create a test email
        email = self.EmailValidation.create({
            'name': 'sendpulse@example.com',
        })

        # Mock token request (successful)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'test_access_token'
        }

        # Mock email validation request (successful)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'success': True,
            'data': {
                'status': 'valid'
            }
        }

        # Test validation
        result = self.sendpulse_validator.validate_email_sendpulse(email)
        self.assertTrue(
            result,
            "SendPulse validation should succeed with valid response")

        # Check token request
        mock_post.assert_called_once_with(
            'https://api.sendpulse.com/oauth/access_token',
            json={
                'grant_type': 'client_credentials',
                'client_id': 'test_user_id',
                'client_secret': 'test_secret'
            },
            timeout=30
        )

        # Check validation request
        mock_get.assert_called_once_with(
            'https://api.sendpulse.com/emails/check',
            params={'email': 'sendpulse@example.com'},
            headers={'Authorization': 'Bearer test_access_token'},
            timeout=30
        )

    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.post')
    def test_validate_email_sendpulse_token_error(self, mock_post):
        """Test SendPulse API validation with token request error."""
        if not self.sendpulse_validator:
            self.skipTest("SendPulse validator not found in data files")

        # Create a test email
        email = self.EmailValidation.create({
            'name': 'sendpulse_error@example.com',
        })

        # Mock token request (failed)
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {
            'error': 'invalid_client'
        }

        # Test validation
        result = self.sendpulse_validator.validate_email_sendpulse(email)
        self.assertFalse(
            result,
            "SendPulse validation should fail when token request fails")

        # Check that error result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.sendpulse_validator.id),
            ('email_id', '=', email.id),
            ('is_valid', '=', False),
        ])
        self.assertEqual(len(results), 1,
                         "Should store error validation result")

    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.post')
    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.get')
    def test_validate_email_sendpulse_invalid_email(self, mock_get, mock_post):
        """Test SendPulse API validation with invalid email response."""
        if not self.sendpulse_validator:
            self.skipTest("SendPulse validator not found in data files")

        # Create a test email
        email = self.EmailValidation.create({
            'name': 'invalid_sendpulse@example.com',
        })

        # Mock token request (successful)
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'access_token': 'test_access_token'
        }

        # Mock email validation request (invalid email)
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'success': True,
            'data': {
                'status': 'invalid'
            }
        }

        # Test validation
        result = self.sendpulse_validator.validate_email_sendpulse(email)
        self.assertFalse(result,
                         "SendPulse validation should fail for invalid email")

    def test_validate_email_sendpulse_invalid_api_key_format(self):
        """Test SendPulse API validation with invalid API key format."""
        if not self.sendpulse_validator:
            self.skipTest("SendPulse validator not found in data files")

        # Set invalid API key format (missing colon)
        original_key = self.sendpulse_validator.api_key
        self.sendpulse_validator.api_key = 'invalid_key_format'

        try:
            # Create a test email
            email = self.EmailValidation.create({
                'name': 'format_error@example.com',
            })

            # Test validation - should raise ValidationError
            with self.assertRaises(exceptions.ValidationError) as context:
                self.sendpulse_validator.validate_email_sendpulse(email)

            self.assertIn('user_id:secret', str(context.exception))
        finally:
            # Restore original API key
            self.sendpulse_validator.api_key = original_key

    def test_validate_email_sendpulse_no_api_key(self):
        """Test SendPulse API validation without API key."""
        if not self.sendpulse_validator:
            self.skipTest("SendPulse validator not found in data files")

        # Remove API key temporarily
        original_key = self.sendpulse_validator.api_key
        self.sendpulse_validator.api_key = False

        try:
            # Create a test email
            email = self.EmailValidation.create({
                'name': 'no_sendpulse_key@example.com',
            })

            # Test validation - should raise ValidationError
            with self.assertRaises(exceptions.ValidationError) as context:
                self.sendpulse_validator.validate_email_sendpulse(email)

            self.assertIn('API key is required', str(context.exception))
        finally:
            # Restore API key
            self.sendpulse_validator.api_key = original_key

    @patch(
        'odoo.addons.kw_email_validation.models.email_validator.requests.post')
    def test_validate_email_sendpulse_exception(self, mock_post):
        """Test SendPulse API validation with network exception."""
        if not self.sendpulse_validator:
            self.skipTest("SendPulse validator not found in data files")

        # Create a test email
        email = self.EmailValidation.create({
            'name': 'sendpulse_exception@example.com',
        })

        # Mock network exception
        mock_post.side_effect = Exception("Network error")

        # Test validation
        result = self.sendpulse_validator.validate_email_sendpulse(email)
        self.assertFalse(result,
                         "SendPulse validation should fail on network "
                         "exception")

        # Check that error result was stored
        results = self.env['kw.email.validation.result'].search([
            ('validator_id', '=', self.sendpulse_validator.id),
            ('email_id', '=', email.id),
            ('is_valid', '=', False),
        ])
        self.assertEqual(len(results), 1,
                         "Should store error validation result")
