import logging

from odoo import models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    """Extend CRM Lead/Opportunity with email validation."""
    _name = 'crm.lead'
    _inherit = ['kw.email.validation.mixin', 'crm.lead', ]
    _kw_email_validation_field = 'email_from'
