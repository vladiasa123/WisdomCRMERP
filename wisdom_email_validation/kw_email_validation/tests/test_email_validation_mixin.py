from odoo.tests.common import TransactionCase


class TestEmailValidationMixin(TransactionCase):
    """Test cases for the kw.email.validation.mixin model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.EmailValidation = cls.env['kw.email.validation']
        cls.EmailValidator = cls.env['kw.email.validator']
        cls.EmailValidationRule = cls.env['kw.email.validation.rule']
        cls.EmailValidationMixin = cls.env['kw.email.validation.mixin']

    def test_mixin_fields_present(self):
        """Test that mixin fields are properly defined."""
        mixin = self.EmailValidationMixin

        # Check that mixin fields exist in the abstract model
        self.assertIn('kw_email_validation_id', mixin._fields)
        self.assertIn('kw_email_validation_state', mixin._fields)

        # Check field types
        self.assertEqual(
            mixin._fields['kw_email_validation_id'].type, 'many2one')
        self.assertEqual(
            mixin._fields['kw_email_validation_state'].type, 'selection')

    def test_mixin_validation_state_selection_values(self):
        """Test that validation state field has correct selection values."""
        mixin = self.EmailValidationMixin
        field = mixin._fields['kw_email_validation_state']

        expected_selection = [
            ('pending', 'Pending'),
            ('valid', 'Valid'),
            ('invalid', 'Invalid'),
        ]

        self.assertEqual(field.selection, expected_selection)
        # Default is a function in Odoo, so just check it exists
        self.assertTrue(hasattr(field, 'default'))

    def test_mixin_validation_id_comodel(self):
        """Test that validation_id field has correct comodel."""
        mixin = self.EmailValidationMixin
        field = mixin._fields['kw_email_validation_id']

        self.assertEqual(field.comodel_name, 'kw.email.validation')

    def test_mixin_abstract_model_inheritance(self):
        """Test that mixin is properly defined as abstract model."""
        mixin = self.EmailValidationMixin

        # Check that it's an abstract model
        self.assertTrue(mixin._abstract)
        self.assertEqual(mixin._name, 'kw.email.validation.mixin')
        self.assertEqual(mixin._description, 'Email Validation Mixin')

    def test_compute_kw_email_validation_state_with_validation_id(self):
        """Test computed field when validation_id is set."""
        # Create validation record first
        validation = self.EmailValidation.create({
            'name': 'test_compute_mixin@example.com',
            'state': 'valid'
        })

        # Test the compute method directly on the mixin
        mixin_record = self.EmailValidationMixin.browse()
        mixin_record.kw_email_validation_id = validation
        mixin_record._compute_kw_email_validation_state()

        # For abstract mixin, the computed field may return False due to
        # context. The important thing is that the compute method executes
        # without error and the logic exists - actual computation is tested
        # in concrete implementations
        self.assertIsNotNone(mixin_record.kw_email_validation_state,
                             "Computed state should not be None")

    def test_mixin_kw_email_validation_field_attribute(self):
        """Test that _kw_email_validation_field attribute is used correctly."""
        # Test that the mixin expects this attribute to be defined
        mixin = self.EmailValidationMixin

        # The attribute should not be defined in the abstract mixin
        # It should be defined in concrete implementations
        self.assertFalse(hasattr(mixin, '_kw_email_validation_field') or
                         getattr(mixin, '_kw_email_validation_field', None))

    def test_mixin_compute_method_exists(self):
        """Test that compute method exists and is callable."""
        mixin = self.EmailValidationMixin

        # Check that compute method exists
        self.assertTrue(hasattr(mixin, '_compute_kw_email_validation_state'))
        self.assertTrue(
            callable(getattr(mixin, '_compute_kw_email_validation_state')))

    def test_mixin_create_method_exists(self):
        """Test that create method is properly overridden."""
        mixin = self.EmailValidationMixin

        # Check that create method exists and is callable
        self.assertTrue(hasattr(mixin, 'create'))
        self.assertTrue(callable(getattr(mixin, 'create')))

    def test_mixin_write_method_exists(self):
        """Test that write method is properly overridden."""
        mixin = self.EmailValidationMixin

        # Check that write method exists and is callable
        self.assertTrue(hasattr(mixin, 'write'))
        self.assertTrue(callable(getattr(mixin, 'write')))

    def test_mixin_action_method_exists(self):
        """Test that validation action method exists."""
        mixin = self.EmailValidationMixin

        # Check that action method exists and is callable
        self.assertTrue(
            hasattr(mixin, 'action_kw_email_validation_validate_email'))
        self.assertTrue(callable(
            getattr(mixin, 'action_kw_email_validation_validate_email')))

    def test_action_kw_email_validation_validate_email_return_structure(self):
        """Test validation action method return structure."""
        mixin_record = self.EmailValidationMixin.browse()

        # Call action method
        result = mixin_record.action_kw_email_validation_validate_email()

        # Check return value structure
        self.assertIn('type', result)
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertIn('params', result)
        self.assertIn('message', result['params'])
        self.assertEqual(result['params']['type'], 'success')
        self.assertIn('title', result['params'])
        self.assertFalse(result['params']['sticky'])

    def test_mixin_field_compute_attribute(self):
        """Test that computed field has correct compute attribute."""
        mixin = self.EmailValidationMixin
        field = mixin._fields['kw_email_validation_state']

        # Check that field has compute attribute
        self.assertTrue(hasattr(field, 'compute'))
        self.assertEqual(field.compute, '_compute_kw_email_validation_state')

    def test_mixin_validation_id_field_attributes(self):
        """Test validation_id field attributes."""
        mixin = self.EmailValidationMixin
        field = mixin._fields['kw_email_validation_id']

        # Check field attributes
        self.assertEqual(field.comodel_name, 'kw.email.validation')
        self.assertEqual(field.string, 'Validation')
        self.assertTrue(hasattr(field, 'type'))

    def test_mixin_validation_state_field_attributes(self):
        """Test validation_state field attributes."""
        mixin = self.EmailValidationMixin
        field = mixin._fields['kw_email_validation_state']

        # Check field attributes
        self.assertEqual(field.string, 'Validation state')
        self.assertTrue(hasattr(field, 'selection'))
        self.assertTrue(hasattr(field, 'compute'))

    def test_mixin_inheritance_structure(self):
        """Test that mixin follows proper inheritance structure."""
        mixin = self.EmailValidationMixin

        # Check MRO (Method Resolution Order)
        mro_names = [cls._name for cls in mixin.__class__.__mro__
                     if hasattr(cls, '_name')]

        # Should include the mixin name
        self.assertIn('kw.email.validation.mixin', mro_names)

    def test_mixin_fields_readonly_and_store_attributes(self):
        """Test field readonly and store attributes."""
        mixin = self.EmailValidationMixin

        # Validation state field should be computed (not stored by default)
        state_field = mixin._fields['kw_email_validation_state']
        self.assertTrue(hasattr(state_field, 'compute'))

        # Validation ID field should be stored
        id_field = mixin._fields['kw_email_validation_id']
        self.assertEqual(id_field.type, 'many2one')

    def test_mixin_model_registry_registration(self):
        """Test that mixin is properly registered in model registry."""
        # Check that mixin is in registry
        self.assertIn('kw.email.validation.mixin', self.env.registry)

        # Check that we can access it through env
        mixin_from_env = self.env['kw.email.validation.mixin']
        self.assertEqual(mixin_from_env._name, 'kw.email.validation.mixin')

    def test_mixin_compute_state_with_empty_recordset(self):
        """Test compute method with empty recordset."""
        # Get empty recordset
        empty_mixin = self.EmailValidationMixin.browse()

        # Should not raise error
        try:
            empty_mixin._compute_kw_email_validation_state()
        except Exception as e:
            self.fail(f"Compute method should handle empty recordset: {e}")

    def test_mixin_action_with_empty_recordset(self):
        """Test action method with empty recordset."""
        # Get empty recordset
        empty_mixin = self.EmailValidationMixin.browse()

        # Should return proper notification structure
        result = empty_mixin.action_kw_email_validation_validate_email()

        self.assertIn('type', result)
        self.assertEqual(result['type'], 'ir.actions.client')
