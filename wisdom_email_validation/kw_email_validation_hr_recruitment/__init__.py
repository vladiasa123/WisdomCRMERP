from odoo.addons.kw_email_validation import post_init_hook as validation_hook

from . import models


def post_init_hook(env):
    """Add existing applicant emails to validation queue."""
    validation_hook(env, 'hr.applicant', 'email_from')
