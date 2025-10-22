import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class EmailValidationMixin(models.AbstractModel):
    """Mixin to add email validation capabilities to any model."""
    _name = 'kw.email.validation.mixin'
    _description = 'Email Validation Mixin'

    kw_email_validation_id = fields.Many2one(
        comodel_name='kw.email.validation',
        string='Validation', )
    kw_email_validation_state = fields.Selection(
        string='Validation state',
        selection=[
            ('pending', 'Pending'),
            ('valid', 'Valid'),
            ('invalid', 'Invalid'),
        ],
        default='pending',
        compute='_compute_kw_email_validation_state', )

    def _compute_kw_email_validation_state(self):
        for record in self:
            if self.kw_email_validation_id:
                record.kw_email_validation_state = \
                    self.kw_email_validation_id.state
                continue
            record.kw_email_validation_state = \
                self.env['kw.email.validation'].sudo().get_validation_state(
                    getattr(record, self._kw_email_validation_field))

    def write(self, vals):
        if self._kw_email_validation_field in vals:
            ev = self.env['kw.email.validation'].sudo()
            validation = ev.get_validation(
                vals.get(self._kw_email_validation_field))
            vals['kw_email_validation_id'] = (
                validation.id if validation else False)
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._kw_email_validation_field in vals:
                ev = self.env['kw.email.validation'].sudo()
                validation = ev.get_validation(
                    vals.get(self._kw_email_validation_field))
                vals['kw_email_validation_id'] = (
                    validation.id if validation else False)
        return super().create(vals_list)

    def action_kw_email_validation_validate_email(self):
        for record in self:
            email_field = getattr(
                record, self._kw_email_validation_field, False)
            if not email_field:
                continue

            validation = self.env['kw.email.validation'].sudo().get_validation(
                email_field)

            if validation:
                validation.validate_email()
                record.kw_email_validation_id = validation.id

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Email Validation'),
                'message': _('Email validation process started.'),
                'sticky': False,
                'type': 'success',
            }
        }
