from odoo import models, fields
import uuid

class Voluntar(models.Model):
    _name = "res.voluntar"
    _description = "Voluntar"

    employee_id = fields.Many2one('hr.employee', string="Employee")
    user_id = fields.Many2one('res.users', string="Related User")
    nume = fields.Char(string="Nume complet", size=100)
    email = fields.Char(string="Email", size=100)
    telefon = fields.Char(string="Telefon", size=20)
    oras = fields.Char(string="Oraș", size=50)
    judet = fields.Char(string="Județ", size=50)
    strada = fields.Char(string="Stradă", size=100)
    numar = fields.Char(string="Număr", size=10)
    serie_buletin = fields.Char(string="Serie buletin", size=10)
    numar_buletin = fields.Char(string="Număr buletin", size=10)
    cod_postal = fields.Char(string="Cod poștal", size=10)
    data_nasterii = fields.Date(string="Data nașterii")
    cnp = fields.Char(string="CNP", size=13)
    abilitati = fields.Text(string="Abilități")
    preferinte = fields.Text(string="Preferințe")
    disponibilitate = fields.Text(string="Disponibilitate")
    date_from = fields.Date(string="Disponibil din")
    date_to = fields.Date(string="Disponibil până la")

    status = fields.Selection(
        [
            ('activ', 'Activ'),
            ('inactiv', 'Inactiv'),
            ('nou', 'Nou'),
            ('suspendat', 'Suspendat'),
        ],
        string="Status",
        default='nou'
    )

    data_inregistrare = fields.Datetime(
        string="Data înregistrării",
        default=fields.Datetime.now,
        readonly=True
    )
