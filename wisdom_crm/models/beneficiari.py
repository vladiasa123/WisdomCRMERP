from odoo import models, fields, api

class Beneficiari(models.Model):
    _name = 'beneficiari.management'
    _description = 'Beneficiari Management'

    # Personal Information
    nume = fields.Char(string='Nume', required=True)
    prenume = fields.Char(string='Prenume', required=True)
    cnp = fields.Char(string='CNP')
    telefon = fields.Char(string='Telefon')
    email = fields.Char(string='Email')
    fisa_servicii_ids = fields.One2many('fisa.servicii', 'beneficiar_id', string="Fise de servicii")

    activitate_ids = fields.Many2many(
        'beneficiar.activitate',
        string="Activități",
        help="Activități asociate beneficiarului"
    )

    
    # Address
    localitate = fields.Char(string='Localitate')
    judet = fields.Char(string='Județ')
    strada = fields.Char(string='Strada')
    numar = fields.Char(string='Număr')
    bloc = fields.Char(string='Bloc')
    scara = fields.Char(string='Scara')
    apartament = fields.Char(string='Apartament')
    resedinta = fields.Selection([('urban', 'Urban'), ('rural', 'Rural')], string='Reședință')
    
    # Education & Work
    ultima_scoala = fields.Char(string='Ultima școală absolvită')
    ocupatie = fields.Char(string='Ocupația')
    calificare = fields.Char(string='Calificare deținută')
    loc_munca = fields.Char(string='Loc de muncă')
    
    # Special attributes
    etnie_roma = fields.Selection([('da', 'DA'), ('nu', 'NU')], string='Etnie romă')
    dizabilitati = fields.Selection([('da', 'DA'), ('nu', 'NU')], string='Persoană cu dizabilități')
    
    # System fields
    date_joined = fields.Date(string='Date Joined', default=fields.Date.context_today)
    status = fields.Selection([
        ('new', 'New'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='new')
    
    notes = fields.Text(string='Notes')

    @api.model
    def action_activate(self):
        """Example server action to activate a beneficiary"""
        for rec in self:
            rec.status = 'active'
