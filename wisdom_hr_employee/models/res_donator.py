from odoo import models, fields, api



class ResDonator(models.Model):
    _name = 'res.donator'
    _description = 'Donator'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    user_id = fields.Many2one('res.users', string="User")
    nume = fields.Char(string="Nume")
    tip = fields.Selection([('persoana_fizica','Persoana Fizica'), ('persoana_juridica','Persoana Juridica')])
    telefon = fields.Char(string="Telefon")
    adresa = fields.Text(string="Adresă")
    preferinte_donatie = fields.Text(string="Preferințe Donație")
    cont_creat_la = fields.Datetime(string="Cont creat la")
    status = fields.Selection([('activ','Activ'),('inactiv','Inactiv'),('potential','Potentia')])
