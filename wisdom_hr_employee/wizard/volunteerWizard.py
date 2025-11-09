from odoo import models, fields, api
import io
import base64
import json
import pdfplumber
from openai import OpenAI
from odoo.exceptions import UserError
from datetime import date
from dotenv import load_dotenv
import os
import re

class VolunteerDataWizard(models.TransientModel):
    _name = "volunteer.data.wizard"
    _description = "Upload Volunteer Data"

    file_data = fields.Binary(string="Upload File", required=True)
    file_name = fields.Char(string="Filename")

    def extract_text_from_pdf(self, pdf_data):
        load_dotenv()
        text = ""
        # pdf_data is base64-encoded binary from Odoo
        pdf_bytes = base64.b64decode(pdf_data)
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text.strip()

    def action_import(self):
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        text = self.extract_text_from_pdf(self.file_data)
        client = OpenAI(api_key=OPENAI_API_KEY)


        today = date.today().strftime("%Y-%m-%d")  # Current date for "prezent"

        prompt = f"""
Am următorul text extras dintr-un fișier PDF. 
Te rog să extragi și să structurezi informațiile în format JSON:

{{
"identitate": {{
    "nume_complet": "string",
    "data_nasterii": "string (YYYY-MM-DD sau gol dacă nu există)",
    "email": "string",
    "telefon": "string"
}},
"abilitati": ["string"],
"domenii_interes": ["string"],
"disponibilitate": "string (ex: part-time, weekend, full-time)",
"educatie": [
    {{ "institutie": "string", "program": "string", "ani": "string" }}
],
"experienta": [
    {{ "rol": "string", "organizatie": "string", "perioada": "string" }}
]
}}

Cerințe suplimentare:
- Normalizează toate datele perioadei în format YYYY-MM-DD.
- Normalizeaza perioada de la pana la cu ' to ' (ex: '2019-01-01 to 2021-12-31').
- Dacă perioada conține 'în curs', 'prezent' sau echivalent, înlocuiește cu {today}.
- Nu inventa date lipsă; lasă câmpul gol sau array gol.
- Normalizează limbajul (ex: abilități cu litere mici).
- Returnează doar JSON valid, fără explicații.

Text extras din PDF:
\"\"\"{text}\"\"\"
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract JSON from response safely
            raw_text = response.choices[0].message.content.strip()
            match = re.search(r'({.*})', raw_text, re.DOTALL)
            if not match:
                raise UserError("OpenAI returned invalid JSON:\n" + raw_text)
            json_text = match.group(1)

            data = json.loads(json_text)
            print("\nParsed JSON dict:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # --- Create experience lines for the current employee ---
            employee_id = self.env.context.get('active_id')
            if not employee_id:
                raise UserError("No employee selected in context!")
            employee = self.env['hr.employee'].browse(employee_id)
            if not employee:
                raise ValueError("Current user does not have an employee record!")

            # Experience
            for exp in data.get("experienta", []):
                date_start, date_end = (False, False)
                perioada = exp.get('perioada', '').strip()
                if perioada:
                    parts = perioada.split(' to ')
                    if len(parts) > 0:
                        date_start = parts[0].strip()
                    if len(parts) > 1:
                        end_raw = parts[1].strip().lower()
                        if end_raw in ["în curs", "prezent", "current", "ongoing"]:
                            date_end = today
                        else:
                            date_end = parts[1].strip()

                self.env['hr.resume.line'].create({
                    'employee_id': employee.id,
                    'name': exp.get('organizatie', ''),
                    'description': exp.get('rol', ''),
                    'date_start': date_start or False,
                    'date_end': date_end or False,
                })

            # Education
            for edu in data.get("educatie", []):
                start_date, end_date = (False, False)
                ani = edu.get('ani', '').strip()
                if ani:
                    parts = ani.split(' to ')
                    if len(parts) > 0:
                        start_date = parts[0].strip()
                    if len(parts) > 1:
                        end_raw = parts[1].strip().lower()
                        if end_raw in ["în curs", "prezent", "current", "ongoing"]:
                            end_date = today
                        else:
                            end_date = parts[1].strip()
                # Optional: create a record in a custom education model or log
                # Example:
                # self.env['hr.education.line'].create({...})

            print(f"{len(data.get('experienta', []))} experience lines created for {employee.name}")

        except json.JSONDecodeError as e:
            raise UserError(f"Eroare la parsarea JSON: {e}")
        except Exception as e:
            raise UserError(f"A apărut o eroare: {e}")