import logging

from odoo import models

_logger = logging.getLogger(__name__)


class HrApplicant(models.Model):
    """Extend HR Applicant with email validation."""
    _name = 'hr.applicant'
    _inherit = ['kw.email.validation.mixin', 'hr.applicant', ]
    _kw_email_validation_field = 'email_from'
