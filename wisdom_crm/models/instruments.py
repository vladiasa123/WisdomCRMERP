from odoo import models, fields

class Instrument(models.Model):
    _name = 'instrumente.instrument'
    _description = 'Instrument'

    name = fields.Char(string='Denumire Instrument', required=True)
    type = fields.Selection([
        ('tool', 'Tool'),
        ('device', 'Device'),
        ('other', 'Altele')
    ], string='Tip', required=True, default='other')
    file = fields.Binary(string='Document')
    file_name = fields.Char(string='Nume fișier')
