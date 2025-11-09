from odoo import models, fields, api
from odoo.exceptions import UserError
import os
import json
import io
import base64

from openai import OpenAI
from PyPDF2 import PdfReader, PdfWriter
from dotenv import load_dotenv
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    user_type = fields.Selection(
        selection=[
            ('angajat', 'Angajat'),
            ('voluntar', 'Voluntar'),
            ('donator', 'Donator'),
        ],
        string='User Type',
    )

    # Links to other models
    donator_id = fields.Many2one('res.donator', string="Donator")
    voluntar_id = fields.Many2one('res.voluntar', string="Voluntar")
    angajat_id = fields.Many2one('res.angajat', string="Angajat")

    # ------------------------------
    # Donator related fields
    # ------------------------------
    nume = fields.Char(related='donator_id.nume', string="Nume Donator", readonly=True)
    tip = fields.Selection(related='donator_id.tip', string="Tip", readonly=True)
    telefon = fields.Char(related='donator_id.telefon', string="Telefon Donator", readonly=True)
    adresa = fields.Text(related='donator_id.adresa', string="Adresă Donator", readonly=True)
    preferinte_donatie = fields.Text(related='donator_id.preferinte_donatie', string="Preferințe Donație", readonly=True)
    cont_creat_la = fields.Datetime(related='donator_id.cont_creat_la', string="Cont creat la", readonly=True)
    status = fields.Selection(related='donator_id.status', string="Status", readonly=True)

    # ------------------------------
    # Voluntar related fields
    # ------------------------------
    voluntar_nume = fields.Char(related='voluntar_id.nume', string="Nume Voluntar", readonly=True, required=False)
    voluntar_telefon = fields.Char(related='voluntar_id.telefon', string="Telefon Voluntar", readonly=True)
    voluntar_data_nasterii = fields.Date(related='voluntar_id.data_nasterii', string="Data nașterii", readonly=True)
    voluntar_cnp = fields.Char(related='voluntar_id.cnp', string="CNP", readonly=True)
    voluntar_abilitati = fields.Text(related='voluntar_id.abilitati', string="Abilități", readonly=True)
    voluntar_preferinte = fields.Text(related='voluntar_id.preferinte', string="Preferințe", readonly=True)
    voluntar_disponibilitate = fields.Text(related='voluntar_id.disponibilitate', string="Disponibilitate", readonly=True)
    voluntar_status = fields.Selection(related='voluntar_id.status', string="Status Voluntar", readonly=True)
    voluntar_data_inregistrare = fields.Datetime(related='voluntar_id.data_inregistrare', string="Data înregistrării", readonly=True)
    voluntar_strada = fields.Char(related='voluntar_id.strada', string="Stradă", readonly=False)
    voluntar_numar = fields.Char(related='voluntar_id.numar', string=" Număr", readonly=False)
    voluntar_judet = fields.Char(related='voluntar_id.judet', string="Județ", readonly=False)
    voluntar_serie_buletin = fields.Char(related='voluntar_id.serie_buletin', string="Serie buletin", readonly=False)
    voluntar_numar_buletin = fields.Char(related='voluntar_id.numar_buletin', string="Număr buletin", readonly=False)
    voluntar_oras = fields.Char(related='voluntar_id.oras', string="Oraș", readonly=False)
    voluntar_date_from = fields.Date(related='voluntar_id.date_from', string="Disponibil din")
    voluntar_date_to = fields.Date(related='voluntar_id.date_to', string="Disponibil până la")


    # ------------------------------
    # Angajat related fields
    # ------------------------------
    angajat_nume = fields.Char(related='angajat_id.nume', string="Nume Angajat", readonly=True)
    angajat_prenume = fields.Char(related='angajat_id.prenume', string="Prenume Angajat", readonly=True)
    angajat_cnp = fields.Char(related='angajat_id.cnp', string="CNP", readonly=True)
    angajat_telefon = fields.Char(related='angajat_id.telefon', string="Telefon Angajat", readonly=True)
    angajat_departament = fields.Many2one(related='angajat_id.departament_id', string="Departament", readonly=True)
    angajat_rol = fields.Char(related='angajat_id.rol', string="Rol", readonly=True)
    angajat_superior = fields.Many2one(related='angajat_id.superior_id', string="Superior direct", readonly=True)


    # Toate datele userului is in self, daca vrei sa vezi ce primesti in self, fa un print(self) si vezi ce contine
    # 1. Daca vrei sa trimiti un email, foloseste self.user_id.email
    # 2. Daca vrei sa vezi ce tip de user e, foloseste self.user_type
    # 3. Daca vrei sa vezi datele donatorului, foloseste self.donator_id
    # 4. Daca vrei sa vezi datele voluntarului, foloseste self.voluntar_id
    # 5. Daca vrei sa vezi datele angajatului, foloseste self.angajat_id


    def action_volunteer_data_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Volunteer Data',
            'res_model': 'volunteer.data.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_user_id': self.id},
        }
    
    def send_email_action(self):
        donator_name = self.nume
        OPENAI_API_KEY_HR = os.getenv("OPENAI_API_KEY_HR")
        donator_tip = self.tip
        donator_campanie = "Campanie de dormit"  # Exemplu, în realitate ar trebui să fie din context
        donator_perioada = "19.10.2025 - 25.10.2025"  # Exemplu, în realitate ar trebui să fie din context
        client = OpenAI(api_key=OPENAI_API_KEY_HR)

        response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ești un generator de emailuri de mulțumire pentru donatori. "
                            "Răspunzi exclusiv în limba română. "
                            "Răspunsul trebuie să fie STRICT JSON valid, fără text în afara obiectului JSON."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"""Ai la dispoziție trei variabile: 
            {{"nume": "{donator_name}"}}, 
            {{"tip": "{donator_tip}"}}, 
            {{"campanie": "{donator_campanie}"}}, 
            {{"perioada": "{donator_perioada}"}}.

            Generează un singur e-mail de mulțumire conform acestei scheme:

            {{
            "subiect": "string",
            "email_text": {{
                "plain": "string",
                "html": "string"
            }},
            "incheiere": "string",
            "semnatura": "string",
            "metadate": {{
                "subiect": "string",
                "lungime_cuvinte_estimata": "int",
                "ton": "string"
            }}
            }}

            Nu adăuga explicații, doar obiectul JSON completat.
            """
                    }
                ]
            )

        content = response.choices[0].message.content
        try:
            data = json.loads(content)
            # get recipient email
            recipient = self.email
            if not recipient:
                raise UserError("Utilizatorul nu are email setat.")

            # build mail values
            mail_values = {
                'subject': data.get("subiect", "Mesaj de mulțumire"),
                'body_html': data["email_text"]["html"],
                'body': data["email_text"]["plain"],  # optional plain version
                'email_to': recipient,
                'author_id': self.env.user.partner_id.id,  # current Odoo user
            }

            # send email
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
        except Exception as e:
            print("\nNu am putut parsa JSON:", e)



    @api.onchange('user_type')
    def _onchange_user_type(self):
        """Auto-link to domain model if it exists"""
        if self.user_type == 'donator':
            self.donator_id = self.env['res.donator'].search([('employee_id', '=', self.id)], limit=1)
        elif self.user_type == 'voluntar':
            self.voluntar_id = self.env['res.voluntar'].search([('employee_id', '=', self.id)], limit=1)
        elif self.user_type == 'angajat':
            self.angajat_id = self.env['res.angajat'].search([('employee_id', '=', self.id)], limit=1)

    def write(self, vals):
        """Keep user_type in sync with linked user"""
        res = super().write(vals)
        if 'user_type' in vals:
            for employee in self:
                if employee.user_id:
                    employee.user_id.write({'user_type': vals['user_type']})
        return res

