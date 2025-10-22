import logging
# pylint: disable=missing-manifest-dependency
import dns.resolver

from odoo import models

_logger = logging.getLogger(__name__)


class EmailValidator(models.Model):
    _inherit = 'kw.email.validator'

    def validate_email_dnspython(self, email, **kwargs):
        domain = email.name.split('@')[-1]
        is_valid = False

        try:
            is_valid = bool(dns.resolver.resolve(domain, 'MX'))
        except Exception as e:
            _logger.debug(e)

        self.store_result(email, is_valid)
        return is_valid
