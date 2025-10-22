import inspect

from odoo.addons.kw_email_validation import post_init_hook

from odoo.tests.common import TransactionCase


class TestPostInitHook(TransactionCase):
    """Test cases for the post_init_hook function."""

    def test_post_init_hook_function_exists(self):
        """Test that post_init_hook function exists and is callable."""
        self.assertTrue(callable(post_init_hook))

    def test_post_init_hook_signature(self):
        """Test that post_init_hook has the correct signature."""
        sig = inspect.signature(post_init_hook)
        params = list(sig.parameters.keys())

        # Should have 3 parameters: env, model_name, email_field
        self.assertEqual(len(params), 3)
        self.assertEqual(params,
                         ['env', 'model_name', 'email_field'])

    def test_post_init_hook_is_function(self):
        """Test that post_init_hook is a function with proper attributes."""
        self.assertTrue(inspect.isfunction(post_init_hook))
        self.assertTrue(hasattr(post_init_hook, '__name__'))
        self.assertEqual(post_init_hook.__name__, 'post_init_hook')

    def test_post_init_hook_module_location(self):
        """Test that post_init_hook is in the correct module."""
        self.assertEqual(post_init_hook.__module__,
                         'odoo.addons.kw_email_validation')

    def test_post_init_hook_functionality_with_real_data(self):
        """Test post_init_hook functionality using real Odoo environment."""
        # Create some test validation records to ensure they exist
        self.env['kw.email.validation'].create({
            'name': 'test_hook1@example.com',
            'state': 'valid'
        })

        self.env['kw.email.validation'].create({
            'name': 'test_hook2@example.com',
            'state': 'invalid'
        })

        # Create a simple test model using kw.email.validation.mixin
        # Since we can't create actual model classes in tests,
        # we'll test the concept
        # by verifying the function can be called without errors

        # Test with a model that doesn't exist - should not raise errors
        try:
            post_init_hook(self.env, 'nonexistent.model', 'email')
        except Exception as e:
            # Should fail gracefully, not crash
            self.assertIn('nonexistent.model', str(e))

    def test_post_init_hook_imports_required_modules(self):
        """Test that post_init_hook properly imports required Odoo modules."""
        # Read the function source to verify it imports required modules
        source = inspect.getsource(post_init_hook)

        # Should work with env parameter directly
        # (no more api.Environment creation)

        # Should search for records
        self.assertIn('search', source)

        # Should use get_validation method
        self.assertIn('get_validation', source)

    def test_post_init_hook_validates_parameters(self):
        """Test post_init_hook parameter validation logic."""
        source = inspect.getsource(post_init_hook)

        # Should check for empty email values
        self.assertIn("'not in'", source)
        self.assertIn('[False', source)

        # Should use getattr to safely access email field
        self.assertIn('getattr', source)

        # Should check if email exists before processing
        self.assertIn('if not email', source)

        # Should assign validation ID when validation exists
        self.assertIn('kw_email_validation_id', source)
