from odoo import models, fields

class BeneficiarCurs(models.Model):
    _name = 'beneficiar.curs'
    _description = 'Alocare curs la beneficiar'

    beneficiari_id = fields.Many2many(
        'beneficiari.management', string='Beneficiar', required=True
    )
    curs_id = fields.Many2one(
        'curs.management', string='Denumire curs', required=True
    )
    data_inceput = fields.Date(string='Data început')
    data_sfarsit = fields.Date(string='Data sfârșit')
    data_certificat = fields.Date(string='Data certificat')
    certificat_file = fields.Binary(string='Încărcare certificat')
    certificat_filename = fields.Char(string='Nume fișier certificat')
