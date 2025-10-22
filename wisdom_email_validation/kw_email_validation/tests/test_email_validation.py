from unittest.mock import patch
from odoo.tests.common import TransactionCase


class TestEmailValidation(TransactionCase):
    """Test cases for the kw.email.validation model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.EmailValidation = cls.env['kw.email.validation']
        cls.EmailValidator = cls.env['kw.email.validator']
        cls.EmailValidationRule = cls.env['kw.email.validation.rule']

        # Create a test validator
        cls.validator = cls.EmailValidator.create({
            'name': 'test_validator',
        })

        # Create a test rule
        cls.rule = cls.EmailValidationRule.create({
            'name': 'Test Rule',
            'validator_id': cls.validator.id,
        })

    def test_get_validation(self):
        """Test the get_validation method."""
        # Test with valid email
        record = self.EmailValidation.get_validation('test@example.com')
        self.assertTrue(record, "Should return a record for valid email")
        self.assertEqual(record.name, 'test@example.com',
                         "Email should be stored in lowercase")
        self.assertEqual(record.state, 'pending',
                         "Initial state should be pending")

        # Test with same email again (should return existing record)
        record2 = self.EmailValidation.get_validation('TEST@example.com')
        self.assertEqual(
            record.id, record2.id,
            "Should return the same record for same email with different case")

        # Test with invalid email format
        record3 = self.EmailValidation.get_validation('invalid-email')
        self.assertFalse(record3,
                         "Should return False for invalid email format")

        # Test with empty email
        record4 = self.EmailValidation.get_validation('')
        self.assertFalse(record4, "Should return False for empty email")

        # Test with None
        record5 = self.EmailValidation.get_validation(None)
        self.assertFalse(record5, "Should return False for None email")

    def test_get_validation_state(self):
        """Test the get_validation_state method."""
        # Test with valid email
        state = self.EmailValidation.get_validation_state('test2@example.com')
        self.assertEqual(state, 'pending',
                         "Initial state should be pending")

        # Test with invalid email format
        state2 = self.EmailValidation.get_validation_state('invalid-email')
        self.assertEqual(state2, 'invalid',
                         "Should return 'invalid' for invalid email format")

        # Test with force_check=True
        state3 = self.EmailValidation.get_validation_state('test3@example.com',
                                                           force_check=True)
        self.assertEqual(state3, 'valid',
                         "Should validate email and return state")

    def test_is_valid(self):
        """Test the is_valid method."""
        # Create a valid email record
        self.EmailValidation.create({
            'name': 'valid@example.com',
            'state': 'valid'
        })

        # Create an invalid email record
        self.EmailValidation.create({
            'name': 'invalid@example.com',
            'state': 'invalid'
        })

        # Test with valid email
        self.assertTrue(
            self.EmailValidation.is_valid('valid@example.com'),
            "Should return True for valid email"
        )

        # Test with invalid email
        self.assertFalse(
            self.EmailValidation.is_valid('invalid@example.com'),
            "Should return False for invalid email"
        )

        # Test with new email (should be pending, thus not valid)
        self.assertFalse(
            self.EmailValidation.is_valid('new@example.com'),
            "Should return False for new email (pending state)"
        )

        # Test with force_check=True
        self.assertTrue(
            self.EmailValidation.is_valid('new2@example.com',
                                          force_check=True),
            "Should validate email and return True if valid"
        )

    def test_create_and_write(self):
        """Test create and write methods."""
        # Test create with uppercase email
        record = self.EmailValidation.create({
            'name': 'TEST@EXAMPLE.COM'
        })
        self.assertEqual(record.name, 'test@example.com',
                         "Email should be stored in lowercase")

        # Test write (should not be able to change email)
        record.write({'name': 'changed@example.com'})
        self.assertEqual(record.name, 'test@example.com',
                         "Email should not be changeable after creation")

    def test_validate_email(self):
        """Test the validate_email method."""
        # Create a test email
        email = self.EmailValidation.create({
            'name': 'test_validate@example.com',
            'state': 'pending'
        })

        # Mock the validator's validate_email method on our specific validator
        # instance
        with patch.object(type(self.validator), 'validate_email',
                          return_value=True) as mock_validate:
            email.validate_email()
            self.assertEqual(
                email.state, 'valid',
                "Email should be marked as valid after validation")
            # Verify that the validator was called
            mock_validate.assert_called()

        # Create another test email
        email2 = self.EmailValidation.create({
            'name': 'test_validate2@example.com',
            'state': 'pending'
        })

        # Mock validator to return False
        with patch.object(type(self.validator), 'validate_email',
                          return_value=False) as mock_validate:
            email2.validate_email()
            self.assertEqual(
                email2.state, 'invalid',
                "Email should be marked as invalid if validation fails")
            # Verify that the validator was called
            mock_validate.assert_called()

    def test_name_get(self):
        """Test the name_get method."""
        # Create a test email
        email = self.EmailValidation.create({
            'name': 'test_name_get@example.com',
            'state': 'valid'
        })

        # Test name_get
        name = email.name_get()[0]
        self.assertEqual(name[1], 'test_name_get@example.com (valid)',
                         "name_get should return email with state")

    def test_action_force_validate_email(self):
        """Test the action_force_validate_email method."""
        # Create a test email
        email = self.EmailValidation.create({
            'name': 'test_action@example.com',
            'state': 'pending'
        })

        # Force validate
        email.action_force_validate_email()
        # The state should be updated by the validation process
        self.assertIn(email.state, ['valid', 'invalid'],
                      "State should be updated after force validation")

    def test_cron_validate_email(self):
        """Test the cron_validate_email method."""
        # Create multiple pending emails
        emails = self.EmailValidation.create([
            {'name': f'cron_test{i}@example.com'} for i in range(5)
        ])

        # Run cron with limit=2
        self.EmailValidation.cron_validate_email(limit=2)

        # Check that at least some emails were processed
        processed = self.EmailValidation.search([
            ('id', 'in', emails.ids),
            ('state', '!=', 'pending')
        ])

        self.assertTrue(len(processed) <= 2,
                        "Cron should process only up to the limit")
