import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class EmailValidationRule(models.Model):
    _name = 'kw.email.validation.rule'
    _description = 'Email Validation'
    _order = 'sequence, id'

    name = fields.Char(
        required=True,
        copy=False, )
    active = fields.Boolean(
        default=True, )
    sequence = fields.Integer(
        default=10, )
    validator_id = fields.Many2one(
        comodel_name='kw.email.validator', )
