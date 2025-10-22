import logging
import smtplib
# pylint: disable=missing-manifest-dependency
import dns.resolver

from odoo import models

_logger = logging.getLogger(__name__)


class EmailValidator(models.Model):
    _inherit = 'kw.email.validator'

    def validate_email_smtp(self, email, **kwargs):
        is_valid = False
        domain = email.name.split('@')[-1]
        smtp = smtplib.SMTP(timeout=30)
        smtp.set_debuglevel(0)
        try:
            hosts = [x.preference for x in dns.resolver.resolve(domain, 'MX')]
        except Exception as e:
            _logger.debug(e)
            self.store_result(email, is_valid)
            return is_valid

        for host in hosts:
            try:
                host = host[0][:-1]
                host = b'.'.join(host).decode('utf-8')
                smtp.connect(host)
                smtp.helo(smtp.local_hostname)
            except Exception as e:
                _logger.debug(e)
                host = False
                continue
            else:
                break

        if not host:
            self.store_result(email, is_valid)
            return is_valid

        try:
            smtp.mail('test@test.test')
            res = smtp.rcpt(email.name)
            smtp.quit()
        except Exception as e:
            _logger.debug(e)
        else:
            is_valid = res[0] == 250

        self.store_result(email, is_valid)
        return is_valid
