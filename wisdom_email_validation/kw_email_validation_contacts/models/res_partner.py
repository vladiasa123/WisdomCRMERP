import logging

from odoo import models

_logger = logging.getLogger(__name__)


class Contact(models.Model):
    _name = 'res.partner'
    _inherit = ['kw.email.validation.mixin', 'res.partner', ]
    _kw_email_validation_field = 'email'
