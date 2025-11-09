from odoo import models, fields, api, _
import logging
from typing import Optional, Dict
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
import re

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    # ------------------------------
    # Extra fields
    # ------------------------------
    user_type = fields.Selection(
        selection=[
            ('angajat', 'Angajat'),
            ('voluntar', 'Voluntar'),
            ('donator', 'Donator'),
        ],
        string='User Type',
        default='voluntar',
    )

    donator_id = fields.Many2one('res.donator', string="Donator")
    voluntar_id = fields.Many2one('res.voluntar', string="Voluntar")
    angajat_id = fields.Many2one('res.angajat', string="Angajat")

    # ------------------------------
    # Donator related (editable)
    # ------------------------------
    nume = fields.Char(related='donator_id.nume', string="Nume", readonly=False)
    tip = fields.Selection(related='donator_id.tip', string="Tip", readonly=False)
    telefon = fields.Char(related='donator_id.telefon', string="Telefon", readonly=False)
    adresa = fields.Text(related='donator_id.adresa', string="Adresă", readonly=False)
    preferinte_donatie = fields.Text(related='donator_id.preferinte_donatie', string="Preferințe Donație", readonly=False)
    cont_creat_la = fields.Datetime(related='donator_id.cont_creat_la', string="Cont creat la", readonly=False)
    status = fields.Selection(related='donator_id.status', string="Status", readonly=False)

    # ------------------------------
    # Voluntar related (editable)
    # ------------------------------
    voluntar_nume = fields.Char(related='voluntar_id.nume', string="Nume Voluntar", readonly=False, required=False)
    voluntar_email = fields.Char(related='voluntar_id.email', string="Email Voluntar", readonly=False)
    voluntar_telefon = fields.Char(related='voluntar_id.telefon', string="Telefon Voluntar", readonly=False)
    voluntar_data_nasterii = fields.Date(related='voluntar_id.data_nasterii', string="Data nașterii", readonly=False)
    voluntar_cnp = fields.Char(related='voluntar_id.cnp', string="CNP", readonly=False)
    voluntar_abilitati = fields.Text(related='voluntar_id.abilitati', string="Abilități", readonly=False)
    voluntar_preferinte = fields.Text(related='voluntar_id.preferinte', string="Preferințe", readonly=False)
    voluntar_disponibilitate = fields.Text(related='voluntar_id.disponibilitate', string="Disponibilitate", readonly=False)
    voluntar_status = fields.Selection(related='voluntar_id.status', string="Status Voluntar", readonly=False)
    voluntar_data_inregistrare = fields.Datetime(related='voluntar_id.data_inregistrare', string="Data înregistrării", readonly=False)
    voluntar_strada = fields.Char(related='voluntar_id.strada', string="Stradă", readonly=False)
    voluntar_numar = fields.Char(related='voluntar_id.numar', string="Număr", readonly=False)
    voluntar_judet = fields.Char(related='voluntar_id.judet', string="Județ", readonly=False)
    voluntar_serie_buletin = fields.Char(related='voluntar_id.serie_buletin', string="Serie buletin", readonly=False)
    voluntar_numar_buletin = fields.Char(related='voluntar_id.numar_buletin', string="Număr buletin", readonly=False)
    voluntar_oras = fields.Char(related='voluntar_id.oras', string="Oraș", readonly=False)
    voluntar_date_from = fields.Date(related='voluntar_id.date_from', string="Disponibil din", readonly=False)
    voluntar_date_to = fields.Date(related='voluntar_id.date_to', string="Disponibil până la", readonly=False)

    # ------------------------------
    # Angajat related (editable)
    # ------------------------------
    angajat_nume = fields.Char(related='angajat_id.nume', string="Nume", readonly=False)
    angajat_prenume = fields.Char(related='angajat_id.prenume', string="Prenume", readonly=False)
    angajat_cnp = fields.Char(related='angajat_id.cnp', string="CNP", readonly=False)
    angajat_email = fields.Char(related='angajat_id.email', string="Email Angajat", readonly=False)
    angajat_telefon = fields.Char(related='angajat_id.telefon', string="Telefon", readonly=False)
    angajat_departament = fields.Many2one(related='angajat_id.departament_id', string="Departament", readonly=False)
    angajat_rol = fields.Char(related='angajat_id.rol', string="Rol", readonly=False)
    angajat_superior = fields.Many2one(related='angajat_id.superior_id', string="Superior direct", readonly=False)
    angajat_function = fields.Selection(related='angajat_id.employee_function', string="Rol Angajat", readonly=False)

    # ------------------------------
    # Document AI helper methods
    # ------------------------------
    def extract_fields(self, document: documentai.Document) -> Dict[str, str]:
        """
        Extracts entities from Document AI response into a dict
        and autofills voluntar fields.
        """
        extracted = {entity.type_: entity.mention_text for entity in document.entities}
        _logger.info("Extracted entities: %s", extracted)

        if self.user_type != 'voluntar':
            return extracted

        vals = {}

        # Name
        if 'Nume' in extracted:
            vals['nume'] = extracted['Nume'].strip()
        if 'CNP' in extracted:
            vals['cnp'] = extracted['CNP'].strip()
        if 'DataNasterii' in extracted:
            vals['data_nasterii'] = extracted['DataNasterii'].strip()
        if 'SerieBuletin' in extracted:
            vals['serie_buletin'] = extracted['SerieBuletin'].strip()
        if 'NumarBuletin' in extracted:
            vals['numar_buletin'] = extracted['NumarBuletin'].strip()

        # Address parsing
        address_text = extracted.get('Domiciliu')
        if address_text:
            address_text = address_text.replace('\n', ', ').replace(';', ',')
            # Extract using regex: "Jud.AB Sat.Bistra (Com.Bistra), Str.Ion Creangă nr.2"
            # Split into parts based on commas
            parts = [p.strip() for p in address_text.split(',') if p.strip()]
            if len(parts) >= 1:
                vals['judet'] = re.search(r'Jud\.\s*([A-Z]+)', parts[0])
                vals['judet'] = vals['judet'].group(1) if vals['judet'] else ''
                vals['oras'] = parts[0].replace(f"Jud.{vals['judet']}", '').strip()
            if len(parts) >= 2:
                vals['strada'] = parts[1]
            if len(parts) >= 3:
                vals['numar'] = parts[2]

        # Create or update voluntar
        if not self.voluntar_id:
            voluntar = self.env['res.voluntar'].create(vals)
            self.voluntar_id = voluntar.id
        else:
            self.voluntar_id.write(vals)

        return extracted

    def process_document_sample(
        self,
        project_id: str,
        location: str,
        processor_id: str,
        file_blob: bytes,
        mime_type: str,
        field_mask: Optional[str] = None,
        processor_version_id: Optional[str] = None,
    ) -> Dict[str, str]:
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts)

        name = client.processor_version_path(project_id, location, processor_id, processor_version_id) \
            if processor_version_id else client.processor_path(project_id, location, processor_id)

        raw_document = documentai.RawDocument(content=file_blob, mime_type=mime_type)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document, field_mask=field_mask)
        result = client.process_document(request=request)
        return self.extract_fields(result.document)

    def action_read_id(self, file_blob: bytes, mime_type: str):
        return self.process_document_sample(
            project_id="779079627865",
            location="eu",
            processor_id="8489c250270ac26c",
            file_blob=file_blob,
            mime_type=mime_type,
        )

    # ------------------------------
    # Overrides & Related Records
    # ------------------------------
    @api.model
    def create(self, vals):
        user = super().create(vals)
        if user.user_type in ('angajat', 'voluntar', 'donator'):
            self._apply_angajat_default_groups(user)
        user._create_related_records(vals)
        return user

    def _apply_angajat_default_groups(self, user):
        xmlids = [
            'base.group_allow_export',
            'base.group_user',
            'account.group_multi_currency',
            'base.group_no_one',
        ]
        group_ids = [g.id for xid in xmlids if (g := self.env.ref(xid, raise_if_not_found=False))]
        if group_ids:
            user.write({'groups_id': [(6, 0, group_ids)]})

    def _create_related_records(self, vals):
        for user in self:
            department_id = False
            if user.user_type == 'donator':
                department_id = self.env['hr.department'].search([('name', '=', 'Donator')], limit=1).id
                if not user.donator_id:
                    donator = self.env['res.donator'].create({
                        'nume': vals.get('nume', user.name),
                        'tip': vals.get('tip', ''),
                        'telefon': vals.get('telefon', ''),
                        'adresa': vals.get('adresa', ''),
                        'preferinte_donatie': vals.get('preferinte_donatie', ''),
                        'cont_creat_la': vals.get('cont_creat_la', False),
                        'status': vals.get('status', ''),
                        'user_id': user.id,
                    })
                    user.donator_id = donator.id

            elif user.user_type == 'voluntar':
                department_id = self.env['hr.department'].search([('name', '=', 'Voluntar')], limit=1).id
                if not user.voluntar_id:
                    voluntar = self.env['res.voluntar'].create({
                        'nume': vals.get('voluntar_nume', ''),
                        'email': vals.get('voluntar_email', ''),
                        'telefon': vals.get('voluntar_telefon', ''),
                        'data_nasterii': vals.get('voluntar_data_nasterii', False),
                        'cnp': vals.get('voluntar_cnp', ''),
                        'abilitati': vals.get('voluntar_abilitati', ''),
                        'strada': vals.get('voluntar_strada', ''),
                        'numar': vals.get('voluntar_numar', ''),
                        'oras': vals.get('voluntar_oras', ''),
                        'judet': vals.get('voluntar_judet', ''),
                        'serie_buletin': vals.get('voluntar_serie_buletin', ''),
                        'numar_buletin': vals.get('voluntar_numar_buletin', ''),
                        'preferinte': vals.get('voluntar_preferinte', ''),
                        'disponibilitate': vals.get('voluntar_disponibilitate', ''),
                        'status': vals.get('voluntar_status', ''),
                        'data_inregistrare': vals.get('voluntar_data_inregistrare', False),
                        'user_id': user.id,
                        'date_from': vals.get('voluntar_date_from', False),
                        'date_to': vals.get('voluntar_date_to', False)
                    })
                    user.voluntar_id = voluntar.id

            elif user.user_type == 'angajat':
                department_id = self.env['hr.department'].search([('name', '=', 'Angajat')], limit=1).id
                if not user.angajat_id:
                    angajat = self.env['res.angajat'].create({
                        'nume': vals.get('angajat_nume', ''),
                        'prenume': vals.get('angajat_prenume', ''),
                        'cnp': vals.get('angajat_cnp', ''),
                        'email': vals.get('angajat_email', ''),
                        'telefon': vals.get('angajat_telefon', ''),
                        'departament_id': vals.get('angajat_departament', False),
                        'rol': vals.get('angajat_rol', ''),
                        'superior_id': vals.get('angajat_superior', False),
                        'user_id': user.id,
                    })
                    user.angajat_id = angajat.id

        return self

    @api.onchange('voluntar_nume', 'donator_id', 'angajat_id')
    def _onchange_update_employee_name(self):
        for user in self:
            employee = self.env['hr.employee'].search([('name', '=', user.name)], limit=1)
            if employee:
                if user.user_type == 'voluntar' and user.voluntar_nume:
                    employee.name = user.voluntar_nume
                elif user.user_type == 'donator' and user.nume:
                    employee.name = user.nume
                elif user.user_type == 'angajat':
                    employee.name = f"{user.angajat_nume or ''} {user.angajat_prenume or ''}".strip()
