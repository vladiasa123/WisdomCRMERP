import logging
import re

import requests

from odoo import models, fields, exceptions, _

_logger = logging.getLogger(__name__)


def use_fname(*deco_args):
    def decorator(func, *aa):
        def wrapper(*args, **kwargs):
            self = args[0]
            self.ensure_one()
            f = deco_args[0] if deco_args else 'code'
            fname = f'{func.__name__}_{getattr(self, f)}'
            if hasattr(self, fname):
                return getattr(self, fname)(*args[1:], **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator


class EmailValidator(models.Model):
    _name = 'kw.email.validator'
    _description = 'Email Validator'

    name = fields.Char(
        required=True, )
    regexp = fields.Char()

    url = fields.Char()

    api_key = fields.Char()

    api_key_visible = fields.Char(
        string='API Key Value',
        related='api_key', )
    is_api_key_visible = fields.Boolean(
        store=False, )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Validator name must be unique!'), ]

    def show_api_key(self):
        self.update({'is_api_key_visible': True})

    def hide_api_key(self):
        self.update({'is_api_key_visible': False})

    @use_fname('name')
    def validate_email(self, email, **kwargs):
        return True

    def store_result(self, email, is_valid, **kwargs):
        self.ensure_one()
        return self.env['kw.email.validation.result'].sudo().create({
            'name': email.name,
            'email_id': email.id,
            'validator_id': self.id,
            'is_valid': is_valid,
            'message': kwargs.get('message')
        })

    def validate_email_regexp(self, email, **kwargs):
        is_valid = bool(re.match(fr'{self.regexp}', email.name))
        self.store_result(email, is_valid)
        return is_valid

    # pylint: disable=too-many-branches
    def _validate_email_url_api_generic(
            self, email, success_condition=None, **kwargs):
        """Generic method for email validation through API URL.

        Args:
            email: Email record to validate
            success_condition: Lambda function to check if
                               response indicates valid email
            **kwargs: Additional parameters for request customization:
                - method: HTTP method (GET or POST)
                - headers: Custom headers for the request
                - data: Data for POST request (will be sent as JSON)
                - auth: Authentication tuple for requests
                - params: URL parameters for GET request

        Returns:
            bool: True if email is valid, False otherwise
        """
        if not self.api_key:
            raise exceptions.ValidationError(_(
                'API key is required to use validator {name}'
                '').format(name=self.name))
        try:
            # Request parameters
            method = kwargs.get('method', 'GET')
            headers = kwargs.get('headers', {})
            data = kwargs.get('data', {})
            auth = kwargs.get('auth', None)
            params = kwargs.get('params', {})

            # If no params provided, use standard format for GET
            if not params and method == 'GET':
                if '{api_key}' in self.url:
                    url = self.url.format(
                        api_key=self.api_key, email=email.name)
                else:
                    url = self.url
                    params['api_key'] = self.api_key
                    params['email'] = email.name
            else:
                url = self.url

            # If no headers provided but Bearer token is needed
            if not headers and kwargs.get('auth_type') == 'bearer':
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }

            # If no data provided for POST request
            if method == 'POST' and not data:
                data = {'email': email.name}

            # Execute request based on method
            if method == 'GET':
                res = requests.get(
                    url, params=params, headers=headers,
                    auth=auth, timeout=30)
            else:  # POST
                res = requests.post(
                    url, json=data, headers=headers,
                    auth=auth, timeout=30)

            is_valid = False
            if res.status_code == 200:
                res_data = res.json()
                if success_condition:
                    is_valid = success_condition(res_data)
                else:
                    is_valid = res_data.get('result') == 'valid'

            self.store_result(email, is_valid, **kwargs)
            return is_valid

        except Exception as e:
            _logger.debug('Error validating email with %s: %s'
                          '', self.name, e)
            self.store_result(email, False)
            return False

    def validate_email_neverbounce(self, email, **kwargs):
        return self._validate_email_url_api_generic(
            email,
            success_condition=lambda res: res.get(
                'status') == 'success' and res.get('result') == 'valid',
            **kwargs
        )

    def validate_email_quickemailverification(self, email, **kwargs):
        return self._validate_email_url_api_generic(
            email,
            success_condition=lambda res: res.get(
                'success') == 'true' and res.get('result') == 'valid',
            **kwargs
        )

    def validate_email_millionverifier(self, email, **kwargs):
        return self._validate_email_url_api_generic(
            email,
            success_condition=lambda res: res.get('status') == 'deliverable',
            **kwargs
        )

    def test_connection(self):
        """Test connection with the validator API.

        This method attempts to validate a test email address to verify
        that the API key is valid and the service is accessible.
        """
        self.ensure_one()

        if not self.api_key:
            return {
                'message': _('API key is required for connection testing.'),
                'success': False, }

        temp_email = False
        try:
            temp_email = self.env['kw.email.validation'].sudo().create({
                'name': 'test@example.com'})

            method_name = f'validate_email_{self.name}'
            if not hasattr(self, method_name):
                return {'message': _('Validation method not found for %s'
                                     '') % self.name,
                        'success': False, }

            getattr(self, method_name)(temp_email)

            result = self.env['kw.email.validation.result'].sudo().search([
                ('email_id', '=', temp_email.id),
                ('validator_id', '=', self.id)
            ], limit=1, order='create_date desc')

            if result:
                return {'message': _('Connection successful! API is '
                                     'working correctly.'),
                        'success': True, }
            return {'message': _('Connection test failed. Validation '
                                 'result not recorded.'),
                    'success': False, }

        except Exception as e:
            return {'message': _('Connection error: %s') % str(e),
                    'success': False, }
        finally:
            if temp_email and hasattr(temp_email, 'result_ids'):
                # Delete related validation results first to avoid foreign key
                # constraint violation
                temp_email.result_ids.sudo().unlink()
                temp_email.sudo().unlink()

    def action_test_connection(self):
        self.ensure_one()

        result = self.test_connection()
        notification_type = 'success' if result['success'] else 'danger'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Connection Test Result'),
                'message': result['message'],
                'sticky': False,
                'type': notification_type,
            }
        }

    def validate_email_clearout(self, email, **kwargs):
        return self._validate_email_url_api_generic(
            email,
            method='POST',
            auth_type='bearer',
            data={'email': email.name},
            success_condition=lambda res: res.get(
                'data', {}).get('status') == 'deliverable',
            **kwargs
        )

    def validate_email_mailercheck(self, email, **kwargs):
        return self._validate_email_url_api_generic(
            email,
            method='POST',
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key
            },
            data={'email': email.name},
            success_condition=lambda res: res.get('status') == 'deliverable',
            **kwargs
        )

    def validate_email_mailgun(self, email, **kwargs):
        return self._validate_email_url_api_generic(
            email,
            auth=('api', self.api_key),
            params={'address': email.name},
            success_condition=lambda res: res.get('result') == 'deliverable',
            **kwargs
        )

    def validate_email_sendpulse(self, email, **kwargs):
        """Validate email using SendPulse API.

        SendPulse API requires a two-step process:
        1. Get token using user_id and secret
        2. Use token to validate email

        API Documentation: https://sendpulse.ua/integrations/api/verifier
        """
        if not self.api_key:
            raise exceptions.ValidationError(_(
                'API key is required to use validator {name}').format(
                name=self.name))

        # SendPulse requires user_id:secret format for API key
        try:
            user_id, secret = self.api_key.split(':')
        except ValueError:
            raise exceptions.ValidationError(_(
                'SendPulse API key must be in format "user_id:secret"'))

        try:
            # Step 1: Get token
            token_url = 'https://api.sendpulse.com/oauth/access_token'
            token_data = {
                'grant_type': 'client_credentials',
                'client_id': user_id,
                'client_secret': secret
            }

            token_res = requests.post(token_url, json=token_data, timeout=30)
            if token_res.status_code != 200:
                self.store_result(email, False)
                return False

            token = token_res.json().get('access_token')
            if not token:
                self.store_result(email, False)
                return False

            # Step 2: Validate email
            headers = {'Authorization': f'Bearer {token}'}
            params = {'email': email.name}

            res = requests.get(self.url, params=params, headers=headers,
                               timeout=30)

            is_valid = False
            if res.status_code == 200:
                res_data = res.json()
                if (res_data.get('success') and
                        res_data.get('data', {}).get('status') == 'valid'):
                    is_valid = True

            self.store_result(email, is_valid)
            return is_valid

        except Exception as e:
            _logger.debug('Error validating email with SendPulse: %s', e)
            self.store_result(email, False)
            return False

    def validate_email_zerobounce(self, email, **kwargs):
        return self._validate_email_url_api_generic(
            email,
            success_condition=lambda res: res.get('status') == 'valid',
            **kwargs
        )
