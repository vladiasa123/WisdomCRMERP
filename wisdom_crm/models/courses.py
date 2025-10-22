from odoo import models, fields, api

class Curs(models.Model):
    _name = 'curs.management'
    _description = 'Curs Management'

    name = fields.Char(string='Denumire curs', required=True)
    tip_curs = fields.Selection([
        ('calificare', 'Calificare'),
        ('specializare', 'Specializare'),
        ('initiere', 'Inițiere'),
        ('formare_interna', 'Formare Internă'),
    ], string='Tip curs', required=True)

    active = fields.Boolean(string='Activ', default=True)

class BeneficiarCurs(models.Model):
    _name = 'beneficiar.curs'
    _description = 'Alocare curs la beneficiar'

    beneficiari_id = fields.Many2one('beneficiari.management', string='Beneficiar', required=True)
    curs_id = fields.Many2one('curs.management', string='Curs', required=True)
    data_inceput = fields.Date(string='Data început')
    data_sfarsit = fields.Date(string='Data sfârșit')
    data_certificat = fields.Date(string='Data certificat')
    certificat_file = fields.Binary(string='Certificat')
    certificat_filename = fields.Char(string='Nume fișier certificat')
