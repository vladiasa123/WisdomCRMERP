from odoo.addons.kw_email_validation import post_init_hook as validation_hook

from . import models


def post_init_hook(env):
    """Add existing event registration emails to validation queue."""
    validation_hook(env, 'event.registration', 'email')
