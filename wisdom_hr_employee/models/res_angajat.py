from odoo import models, fields, api

class ResAngajat(models.Model):
    _name = 'res.angajat'
    _description = 'Angajat'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    user_id = fields.Many2one('res.users', string="User")
    nume = fields.Char(string="Nume", required=True)
    prenume = fields.Char(string="Prenume", required=True)
    cnp = fields.Char(string="CNP", size=13)
    email = fields.Char(string="Email")
    telefon = fields.Char(string="Telefon")
    employee_function = fields.Selection(
        selection=[
            ('conducere', 'Conducere'),
            ('executie', 'Executie'),
        ],
    )

    departament_id = fields.Many2one('hr.department', string="Departament")
    rol = fields.Char(string="Rol")
    superior_id = fields.Many2one('res.angajat', string="Superior direct")
