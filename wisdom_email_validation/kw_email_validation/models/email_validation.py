import logging
from typing import List, Tuple

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class EmailValidation(models.Model):
    """Central email validation service.
    This model serves as the single entry point for email validation.
    It abstracts away the validation implementation details and provides
    a simple interface for checking email validity.
    """
    _name = 'kw.email.validation'
    _description = 'Email Validation'

    name = fields.Char(
        string='Email',
        required=True,
        index=True,
        readonly=True,
        copy=False,
        help='Email address in lowercase', )
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('valid', 'Valid'),
            ('invalid', 'Invalid'),
        ],
        default='pending',
        index=True,
        required=True,
        readonly=True, )
    result_ids = fields.One2many(
        comodel_name='kw.email.validation.result',
        inverse_name='email_id',
        string='Validation Results',
        readonly=True, )

    _sql_constraints = [
        ('email_uniq', 'UNIQUE(name)', 'Email must be unique!')
    ]

    @api.model
    def get_validation(self, email: str) -> str:
        if not email or not isinstance(email, str) or '@' not in email:
            return False

        email = email.strip().lower()
        record = self.sudo().search([('name', '=', email)], limit=1)

        if not record:
            record = self.sudo().create({'name': email})

        return record

    @api.model
    def get_validation_state(
            self, email: str, force_check: bool = False) -> str:
        if not email or not isinstance(email, str) or '@' not in email:
            return 'invalid'

        email = email.strip().lower()
        record = self.sudo().search([('name', '=', email)], limit=1)

        if not record:
            record = self.sudo().create({'name': email})

        if force_check:
            record.validate_email()

        return record.state

    def validate_email(self) -> None:
        """Validate an email using all available validators.
        """
        self.ensure_one()
        rules = self.env['kw.email.validation.rule'].search([])
        if not rules:
            return

        state = 'valid'
        for rule in rules:
            res = rule.validator_id.validate_email(self)

            if not res:
                state = 'invalid'
                break

        if self.state != state:
            self.write({'state': state})
            self.invalidate_recordset()

    @api.model
    def is_valid(self, email: str, force_check: bool = False) -> bool:
        return self.get_validation_state(email, force_check=force_check) \
            == 'valid'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' in vals and vals.get('name'):
                vals['name'] = vals['name'].strip().lower()
        return super().create(vals_list)

    def write(self, vals):
        """Prevent changing email after creation."""
        if 'name' in vals:
            del vals['name']

        if not vals:
            return True

        return super().write(vals)

    def name_get(self) -> List[Tuple[int, str]]:
        """Display email with validation status."""
        return [(record.id, f"{record.name} ({record.state})")
                for record in self]

    def action_force_validate_email(self) -> None:
        """Action to manually trigger email validation."""
        for record in self:
            record.get_validation_state(record.name, True)

    @api.model
    def cron_validate_email(self, limit: int = 10) -> None:
        for record in self.search([('state', '=', 'pending')], limit=limit):
            record.get_validation_state(record.name, True)
