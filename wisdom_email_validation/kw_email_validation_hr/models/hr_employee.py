import logging

from odoo import models

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    """Extend HR Employee with email validation."""
    _name = 'hr.employee'
    _inherit = ['kw.email.validation.mixin', 'hr.employee', ]
    _kw_email_validation_field = 'work_email'
