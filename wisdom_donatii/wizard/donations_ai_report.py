from odoo import models, api
from odoo.exceptions import UserError
import os, io, base64, json
from openai import OpenAI
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class DonationAIReport(models.TransientModel):
    _name = "donation.ai.report"
    _description = "Raport AI pentru Campanii și Donatori"

    def action_generate_ai_report(self):
        """Generate PDF AI report for selected campaigns."""
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError("Nu ai selectat nicio campanie.")

        campaigns = self.env['donation.campaign'].browse(active_ids)

        # Prepare data for AI
        campaigns_data = []
        for c in campaigns:
            donations = self.env['donation.donation'].search([('campaign_id', '=', c.id)])
            donors = {}
            for d in donations:
                if not d.donator_id:
                    continue
                donors.setdefault(d.donator_id.nume, {
                    "tip": d.donator_tip,
                    "status": d.donator_status,
                    "total": 0,
                    "metode": {},
                    "donații": []
                })
                donors[d.donator_id.nume]["total"] += d.amount
                donors[d.donator_id.nume]["metode"][d.method] = donors[d.donator_id.nume]["metode"].get(d.method, 0) + d.amount
                donors[d.donator_id.nume]["donații"].append({
                    "data": str(d.date),
                    "suma": d.amount,
                    "metodă": d.method
                })
            campaigns_data.append({
                "campanie": c.name,
                "activă": c.active,
                "descriere": c.description or "",
                "număr_donații": len(donations),
                "total_donații": sum(d.amount for d in donations),
                "donatori": donors
            })

        # AI prompt
        summary_json = json.dumps(campaigns_data, ensure_ascii=False, indent=2)
        prompt = f"""
Primești date structurate despre campanii de donații și donatori.

{summary_json}

Analizează-le și răspunde cu un JSON de forma:
{{
    "analiza_generala": "string - sumar al tuturor campaniilor",
    "campanii": [
        {{
            "nume": "string",
            "insighturi": "string",
            "top_donatori": ["nume1", "nume2"],
            "trenduri": "string",
            "recomandari": "string"
        }}
    ],
    "recomandari_finale": "string - ce acțiuni strategice să luăm"
}}

Scrie în limba română, fara diacritice. Fără explicații suplimentare, doar JSON valid.
"""

        api_key = os.getenv("OPENAI_API_KEY_HR")
        if not api_key:
            raise UserError("Lipsește cheia OPENAI_API_KEY_HR în mediul serverului Odoo.")

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "Ești un analist de date pentru organizații caritabile."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        try:
            data = json.loads(content)
        except Exception as e:
            raise UserError(f"Eroare la parsarea răspunsului AI: {e}\nRăspuns primit: {content}")

        # Generate PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, y, "Raport AI - Donații și Campanii")
        y -= 40

        p.setFont("Helvetica", 11)
        p.drawString(50, y, "Analiza generală:")
        y -= 20
        text_obj = p.beginText(50, y)
        text_obj.setFont("Helvetica", 10)
        for line in data.get("analiza_generala", "").split("\n"):
            text_obj.textLine(line)
        p.drawText(text_obj)
        y = text_obj.getY() - 20

        for camp in data.get("campanii", []):
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, f"📌 {camp['nume']}")
            y -= 15
            p.setFont("Helvetica", 10)
            for key in ["insighturi", "trenduri", "top_donatori", "recomandari"]:
                val = camp.get(key, "")
                if isinstance(val, list):
                    val = ", ".join(val)
                if y < 100:
                    p.showPage()
                    y = height - 80
                p.drawString(60, y, f"• {key.capitalize()}: {val}")
                y -= 15
            y -= 10

        p.save()
        pdf = buffer.getvalue()
        buffer.close()

        # Create attachment
        attachment_id = self.env['ir.attachment'].create({
            'name': 'Raport_AI.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf),
            'mimetype': 'application/pdf',
            'res_model': 'donation.ai.report',
            'res_id': self.id,
        }).id

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment_id}?download=true',
            'target': 'self',
        }
