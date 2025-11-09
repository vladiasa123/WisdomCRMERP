from odoo import models, fields, api
import io
import base64
import pandas as pd


class Beneficiari(models.Model):
    _name = 'beneficiari.management'
    _description = 'Beneficiari Management'
    _rec_name = 'nume'

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

    # ✅ Combined export of all related data
    def action_export_all_data(self):
        beneficiari = self.search([])
        benef_data = []
        for b in beneficiari:
            benef_data.append({
                'ID': b.id,
                'Nume': b.nume,
                'Prenume': b.prenume,
                'CNP': b.cnp,
                'Telefon': b.telefon,
                'Email': b.email,
                'Localitate': b.localitate,
                'Județ': b.judet,
                'Status': b.status,
            })

        # Courses (Many2many handled safely)
        curs_data = []
        for c in self.env['beneficiar.curs'].search([]):
            beneficiari_nume = (
                ', '.join(c.beneficiari_id.mapped('nume'))
                if c._fields['beneficiari_id'].type == 'many2many'
                else c.beneficiari_id.nume
            )
            curs_data.append({
                'Beneficiar': beneficiari_nume,
                'Curs': c.curs_id.name,
                'Data început': c.data_inceput,
                'Data sfârșit': c.data_sfarsit,
                'Certificat': c.certificat_filename,
            })

        # Service sheets (One2many / Many2one)
        fisa_data = []
        for f in self.env['fisa.servicii'].search([]):
            fisa_data.append({
                'Beneficiar': f.beneficiar_id.nume if f.beneficiar_id else '',
                'Număr fișă': f.numar_fisa,
                'Activitate': f.activitate,
                'Temă': f.tema,
                'Lună/An': f.luna_an,
            })

        # Convert to Excel using pandas
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(benef_data).to_excel(writer, sheet_name='Beneficiari', index=False)
            pd.DataFrame(curs_data).to_excel(writer, sheet_name='Cursuri', index=False)
            pd.DataFrame(fisa_data).to_excel(writer, sheet_name='Fișe Servicii', index=False)
        output.seek(0)

        # Create attachment and download
        attachment = self.env['ir.attachment'].create({
            'name': 'export_beneficiari_complet.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    @api.model
    def action_activate(self):
        """Example server action to activate a beneficiary"""
        for rec in self:
            rec.status = 'active'
