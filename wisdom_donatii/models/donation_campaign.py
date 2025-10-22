# models/donation_campaign.py
from odoo import models, fields

class DonationCampaign(models.Model):
    _name = "donation.campaign"
    _description = "Donation Campaign"

    name = fields.Char(required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    active = fields.Boolean(default=True)
    description = fields.Text()
