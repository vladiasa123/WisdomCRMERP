from odoo import models, fields

class FisaServicii(models.Model):
    _name = 'fisa.servicii'
    _description = 'Fisa de servicii'

    beneficiar_id = fields.Many2one('beneficiari.management', string='Beneficiar', ondelete='cascade')
    activitate = fields.Char(string="Activitate", required=True)
    numar_fisa = fields.Char(string="Numar fisa", required=True)
    tema = fields.Char(string="Tema")
    luna_an = fields.Date(string="Month and Year")
    document = fields.Binary(string="Upload Document")
    filename = fields.Char(string="Filename")
