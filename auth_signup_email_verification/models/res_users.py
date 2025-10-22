# -*- coding: utf-8 -*-

import logging
from odoo import api, models, _

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'



    @api.model
    def signup(self, values, token=None):
        """Override signup to handle email verification completion"""
        
        if token:
            # Verify the token using Odoo's official method
            partner = self.env['res.partner']._signup_retrieve_partner(
                token, check_validity=True, raise_exception=True
            )
            
            # If this is our email verification flow, complete verification
            if partner.signup_type == 'signup' and hasattr(partner, 'email_verified') and not partner.email_verified:
                # Mark email as verified
                partner.complete_email_verification()
                
                # Merge stored user data if available
                if partner.signup_user_data:
                    stored_data = partner.signup_user_data
                    for key, value in stored_data.items():
                        if key not in values or not values.get(key):
                            values[key] = value
                    
                    # Clear stored data
                    partner.write({'signup_user_data': False})
        
        # Call original signup method
        result = super().signup(values, token)
        
        if result:
            login, password = result
            _logger.info("User signup completed successfully: %s", login)
        
        return result 