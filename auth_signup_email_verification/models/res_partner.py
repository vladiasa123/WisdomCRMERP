# -*- coding: utf-8 -*-

import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Email verification flag
    email_verified = fields.Boolean(
        string='Email Verified',
        default=False,
        help="Indicates if the email address has been verified"
    )

    account_type = fields.Selection([
        ('voluntar', 'Voluntar'),
        ('donator', 'Donator'),
        ('employee', 'Employee'),
    ], string='Account Type', store=True)
    
    # Store user data during signup verification
    signup_user_data = fields.Json(
        string='Signup User Data',
        help="Temporary storage for user data during email verification"
    )

    def signup_prepare_with_verification(self, user_data):
        """Prepare signup with email verification step"""
        self.ensure_one()
        
        # Clean user data - remove fields that don't exist on res.users model
        # Keep the custom field for our internal logic but don't pass it to Odoo's signup
        clean_user_data = {
            key: value for key, value in user_data.items()
            if key in ['name', 'login', 'password', 'lang', 'is_company', 'company_name']
        }
        
        # Store clean user data for later use (without signup_company_type)
        self.write({
            'signup_user_data': clean_user_data,
            'signup_type': 'signup',
            'email_verified': False
        })
        
        # Generate signup token using Odoo's official method
        token = self._generate_signup_token()
        
        # Send verification email
        self._send_verification_email()
        
        _logger.info("Email verification initiated for: %s", self.email)
        return self._generate_signup_token()

    def _send_verification_email(self):
        """Send verification email using Odoo's mail template system"""
        self.ensure_one()
        
        if not self.email:
            raise UserError(_('Email address is required for verification.'))
        
        try:
            template = self.env.ref('auth_signup_email_verification.mail_template_email_verification')
            
            # Get partner's language or fallback to English
            partner_lang = self.lang or 'en_US'
            
            # Verify language exists in installed languages
            installed_langs = [code for code, _ in self.env['res.lang'].get_installed()]
            if partner_lang not in installed_langs:
                _logger.warning("Partner language %s not installed, falling back to en_US", partner_lang)
                partner_lang = 'en_US'
            
            _logger.info("Sending verification email in language: %s to: %s", partner_lang, self.email)
            _logger.info("Partner.lang value: %s", self.lang)
            _logger.info("Installed languages: %s", installed_langs)
            
            # Send email using Odoo 18 compatible method
            template.with_context(lang=partner_lang).send_mail(
                self.id,
                force_send=True,
                raise_exception=True
            )
            
            _logger.info("Verification email sent successfully to: %s in language: %s", self.email, partner_lang)
        except Exception as e:
            _logger.error("Failed to send verification email to %s: %s", self.email, str(e))
            raise UserError(_('Failed to send verification email. Please try again.'))

    def get_verification_url(self):
        """Get verification URL for email templates using Odoo's official approach"""
        self.ensure_one()
        
        # Use Odoo's official token generation
        token = self._generate_signup_token()
        
        # Generate custom verification URL
        base_url = self.get_base_url()
        return f"{base_url}/auth/verify/email?token={token}"

    def complete_email_verification(self):
        """Complete email verification and mark as verified"""
        self.ensure_one()
        
        if self.email_verified:
            raise UserError(_('Email has already been verified.'))
        
        # Mark email as verified
        self.write({'email_verified': True})
        
        _logger.info("Email verification completed for: %s", self.email)
        return True

    @api.model
    def create_partner_for_signup(self, email, user_data):
        """Create partner for email verification signup with company/individual support"""
        
        # DEBUG: Log input data
        _logger.info("=== PARTNER CREATION ===")
        _logger.info("email: %s", email)
        _logger.info("user_data: %s", user_data)
        _logger.info("Language from user_data: %s", user_data.get('lang', 'NOT_SET'))
        
        # Check if partner already exists (check by contact email for companies)
        contact_email = email if user_data.get('signup_company_type', 'person') != 'company' else email
        existing_partner = self.search([('email', '=', contact_email)], limit=1)
        if existing_partner:
            if existing_partner.user_ids:
                raise UserError(_('A user with this email already exists.'))
            # Update existing partner
            existing_partner.signup_prepare_with_verification(user_data)
            return existing_partner
        
        # Determine signup type
        company_type = user_data.get('signup_company_type', 'person')
        _logger.info("company_type from user_data: %s", company_type)
        
        if company_type == 'company':
            # Company signup - simplified: create only company record with single email
            company_name = user_data.get('name', 'Company')  # Company name from form
            company_email = email  # Single email for the company (no separate contact)
            
            _logger.info("Creating SIMPLIFIED COMPANY structure:")
            _logger.info("  - company_name: %s", company_name)
            _logger.info("  - company_email: %s", company_email)
            _logger.info("  - NO separate contact person")
            
            # Company record with all fields
            company_vals = {
                'name': company_name, 
                'is_company': True, 
                'email': company_email,  # Single company email
                'lang': user_data.get('lang', 'en_US'),
                'company_id': self.env.company.id,
                # 'customer_rank': 1,  # Mark as customer
            }
            
            # Process dynamic fields from configuration - all go to company
            try:
                all_configs = self.env['ir.config_parameter'].sudo().get_param(
                    'auth_signup_email_verification.all_field_configurations', '{}'
                )
                import json
                dynamic_fields = json.loads(all_configs) if all_configs else {}
                
                # Process all dynamic fields from all models
                for model_name, field_names in dynamic_fields.items():
                    for field_name in field_names:
                        field_value = user_data.get(field_name)
                        if field_value:
                            # DEBUG: Special logging for many2one fields like country_id
                            if field_name == 'country_id':
                                _logger.info("  - COUNTRY_ID DEBUG: raw value = %s (type: %s)", field_value, type(field_value))
                            
                            company_vals[field_name] = field_value
                            _logger.info("  - Added dynamic field: %s = %s", field_name, field_value)
                                
            except Exception as e:
                _logger.warning("Error processing dynamic fields: %s", str(e))
            
            # Create single company partner
            company_partner = self.create(company_vals)
            _logger.info("Created company partner: %s (ID: %s) with language: %s", 
                        company_partner.name, company_partner.id, company_partner.lang)
            
            # Prepare company for verification (user will be created for company directly)
            company_partner.signup_prepare_with_verification(user_data)
            _logger.info("Returning company partner for user creation")
            return company_partner
            
        else:
            # For individual signup: create individual partner
            _logger.info("Creating INDIVIDUAL partner:")
            _logger.info("  - name: %s", user_data.get('name'))
            
            partner = self.create({
                'name': user_data.get('name'),
                'email': email,
                'is_company': False,
                # 'customer_rank': 1,  # Mark as customer
                'lang': user_data.get('lang', 'en_US'),  # Apply language to individual
                'company_id': self.env.company.id  # Set current Odoo company
            })
            _logger.info("Created individual partner: %s (ID: %s) with language: %s", 
                        partner.name, partner.id, partner.lang)
            
            # Prepare for verification
            partner.signup_prepare_with_verification(user_data)
            return partner 