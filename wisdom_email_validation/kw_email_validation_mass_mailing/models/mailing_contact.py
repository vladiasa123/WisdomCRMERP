import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailingContact(models.Model):
    """Extend Mailing Contact with email validation."""
    _name = 'mailing.contact'
    _inherit = ['kw.email.validation.mixin', 'mailing.contact', ]
    _kw_email_validation_field = 'email'
