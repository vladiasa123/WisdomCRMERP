from odoo import models, fields, api


class ActivitateBeneficiar(models.Model):
    _name = 'beneficiar.activitate'
    _description = 'Activitati pentru beneficiari'

    numar = fields.Char(string="Număr Activitate", required=True)
    name = fields.Char(string="Denumire Activitate", required=True)
