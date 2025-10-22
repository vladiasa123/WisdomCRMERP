import logging

from odoo import models

_logger = logging.getLogger(__name__)


class EventRegistration(models.Model):
    """Extend Event Registration with email validation."""
    _name = 'event.registration'
    _inherit = ['kw.email.validation.mixin', 'event.registration', ]
    _kw_email_validation_field = 'email'
