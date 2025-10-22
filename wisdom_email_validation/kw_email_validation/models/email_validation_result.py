import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class EmailValidationResult(models.Model):
    """Stores email validation results for caching and analysis."""
    _name = 'kw.email.validation.result'
    _description = 'Email Validation Result'

    name = fields.Char(
        string='Email Address', )
    email_id = fields.Many2one(
        comodel_name='kw.email.validation',
        required=True,
        index=True, )
    is_valid = fields.Boolean(
        index=True, )
    validator_id = fields.Many2one(
        comodel_name='kw.email.validator',
        ondelete='cascade',
        required=True, )
    message = fields.Text(
        help='Human-readable validation result', )
