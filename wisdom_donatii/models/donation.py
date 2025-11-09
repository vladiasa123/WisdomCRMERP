# models/donation.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Donation(models.Model):
    _name = "donation.donation"
    _description = "Donation"
    _order = "date desc, id desc"

    donator_id = fields.Many2one('res.donator', string="Donator")
    campaign_id = fields.Many2one('donation.campaign', string="Campaign")
    amount = fields.Monetary(string="Amount", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    method = fields.Selection(
        [
            ("cash", "Cash"),
            ("card", "Card"),
            ("bank", "Bank Transfer"),
            ("online", "Online"),
        ],
        string="Method",
        required=True,
        default="cash",
    )
    reference = fields.Char(string="Reference")
    note = fields.Text(string="Notes")

    # Related fields (utile la listă / căutare)
    donator_nume = fields.Char(related="donator_id.nume", store=True, string="Nume Donator")
    donator_tip = fields.Selection(related="donator_id.tip", store=True, string="Tip Donator")
    donator_status = fields.Selection(related="donator_id.status", store=True, string="Status Donator")

    

            
    def action_open_wizard(self):
        if not self:
            raise UserError("Nu ai selectat nicio donație.")

        # Collect unique campaign IDs from selected donations
        campaign_ids = self.mapped('campaign_id').ids
        if not campaign_ids:
            raise UserError("Donațiile selectate nu au campanii asociate.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Donations AI',
            'res_model': 'donation.ai.report',
            'view_mode': 'form',
            'target': 'new',  # Odoo popup dialog
            'context': {
                'default_campaign_id': campaign_ids[0],  # optional default
                'active_ids': campaign_ids,  # pass all selected campaigns to the wizard
            },
        }


    @api.constrains("amount")
    def _check_amount_positive(self):
        for rec in self:
            if rec.amount and rec.amount <= 0:
                raise ValidationError("Amount must be strictly positive.")
