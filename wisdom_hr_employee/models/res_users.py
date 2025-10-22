from odoo import models, fields, api, _
import logging
from typing import Optional, Dict
from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore

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

    # attendance_enabled = fields.Boolean(
    #     string="Attendance Enabled",
    #     help="If checked, the user will be added to the Attendances group."
    # )

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
    voluntar_nume = fields.Char(related='voluntar_id.nume', string="Nume Voluntar", readonly=False)
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
    voluntar_numar = fields.Char(related='voluntar_id.numar', string=" Număr", readonly=False)
    voluntar_judet = fields.Char(related='voluntar_id.judet', string="Județ", readonly=False)
    voluntar_serie_buletin = fields.Char(related='voluntar_id.serie_buletin', string="Serie buletin", readonly=False)
    voluntar_numar_buletin = fields.Char(related='voluntar_id.numar_buletin', string="Număr buletin", readonly=False)
    voluntar_oras = fields.Char(related='voluntar_id.oras', string="Oraș", readonly=False)
    voluntar_date_from = fields.Date(related='voluntar_id.date_from', string="Disponibil din" ,  readonly=False)
    voluntar_date_to = fields.Date(related='voluntar_id.date_to', string="Disponibil până la",   readonly=False)

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
    def extract_fields(document: documentai.Document) -> Dict[str, str]:
        """
        Extracts entities from the Document AI response into a dict
        where the key = entity type and value = mention text.
        """
        fields = {}
        for entity in document.entities:
            fields[entity.type_] = entity.mention_text
        return fields

    def process_document_sample(
        self,
        project_id: str,
        location: str,
        processor_id: str,
        file_blob: bytes,  # <-- changed from file_path
        mime_type: str,
        field_mask: Optional[str] = None,
        processor_version_id: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Process a document using Document AI, from an uploaded blob (binary content).
        file_blob: should be raw bytes (decoded from base64 if coming from Odoo Binary field)
        """
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts)

        # Choose processor or processor version
        if processor_version_id:
            name = client.processor_version_path(project_id, location, processor_id, processor_version_id)
        else:
            name = client.processor_path(project_id, location, processor_id)

        # Send directly the binary blob to Document AI
        raw_document = documentai.RawDocument(content=file_blob, mime_type=mime_type)

        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document,
            field_mask=field_mask,
        )

        result = client.process_document(request=request)
        document = result.document

        extracted = self.extract_fields(document)
        _logger.info("Extracted entities: %s", extracted)
        return extracted

    def action_read_id(self, file_blob: bytes, mime_type: str):
        """
        Wrapper to process uploaded file blob from wizard.
        """
        return self.process_document_sample(
            project_id="779079627865",
            location="eu",
            processor_id="8489c250270ac26c",
            file_blob=file_blob,
            mime_type=mime_type,
        )

    if __name__ == "__main__":
        action_read_id()

    # ------------------------------
    # Overrides
    # ------------------------------
    @api.model
    def create(self, vals):
        user = super().create(vals)

        # Assign the strict group set ONLY for 'angajat'
        if user.user_type in ('angajat', 'voluntar'):
            self._apply_angajat_default_groups(user)

        # Continue your logic
        user._create_related_records(vals)
        return user

    # ------------------------------
    # Group assignment for 'angajat'
    # ------------------------------
    def _apply_angajat_default_groups(self, user):
        """
        Replace user's groups with the exact set required for 'angajat'.
        Adjust XML IDs if your DB differs.
        """
        xmlids = [
            'base.group_allow_export',
            'hr_attendance_reason.group_hr_attendance_user',
            'base.group_user',
            'account.group_multi_currency',
            'hr.group_hr_user',
            'hr_attendance.group_hr_attendance_officer',
            'base.group_no_one',
            'hr_attendance.group_hr_attendance_own_reader',
            'event.group_event_registration_desk'
        ]

        group_ids = []
        for xid in xmlids:
            g = self.env.ref(xid, raise_if_not_found=False)
            if g:
                group_ids.append(g.id)
            else:
                _logger.warning("Default angajat group XML-ID not found: %s", xid)

        if group_ids:
            user.write({'groups_id': [(6, 0, group_ids)]})

    # ------------------------------
    # Related record + employee creation
    # ------------------------------
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
                self.env['hr.employee'].create({
                    'name': user.donator_id.nume,
                    'work_email': getattr(user.donator_id, 'email', False),
                    'user_type': 'donator',
                    'department_id': department_id,
                    'user_id': user.id,
                    'donator_id': user.donator_id.id,
                })

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
                    })
                    user.voluntar_id = voluntar.id
                self.env['hr.employee'].create({
                    'name': user.voluntar_id.nume,
                    'work_email': user.voluntar_id.email,
                    'user_type': 'voluntar',
                    'department_id': department_id,
                    'user_id': user.id,
                    'voluntar_id': user.voluntar_id.id,
                })

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
                self.env['hr.employee'].create({
                    'name': f"{user.angajat_id.nume} {user.angajat_id.prenume}".strip(),
                    'work_email': user.angajat_id.email,
                    'user_type': 'angajat',
                    'department_id': department_id,
                    'user_id': user.id,
                    'angajat_id': user.angajat_id.id,
                })

        return user
