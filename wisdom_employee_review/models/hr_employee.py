from odoo import models, fields, api
from odoo.exceptions import UserError
import io
import base64
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_download_adeverinta_pdf(self):
        """Fill adeverinta PDF with employee data and return download"""
        self.ensure_one()

        # List of required fields
        required_fields = {
            'Name': self.name,
            'Voluntar Oras': self.voluntar_oras,
            'Voluntar Strada': self.voluntar_strada,
            'Voluntar Numar': self.voluntar_numar,
            'Voluntar Judet': self.voluntar_judet,
            'Voluntar Serie Buletin': self.voluntar_serie_buletin,
            'Voluntar Numar Buletin': self.voluntar_numar_buletin,
            'Voluntar CNP': self.voluntar_cnp,
            'Voluntar Date From': self.voluntar_date_from,
            'Voluntar Date To': self.voluntar_date_to,
        }

        # Check for missing fields
        missing = [name for name, value in required_fields.items() if not value]
        if missing:
            raise UserError(
                "The following fields are required to generate the PDF:\n- " +
                "\n- ".join(missing)
            )

        today_date = datetime.today().strftime("%d.%m.%Y")  # Format as dd.mm.yyyy

        # Path to the PDF template
        template_path = "/odoo-18/Adeverinta voluntariat Procivitas.pdf"

        # Read PDF template safely into memory
        with open(template_path, "rb") as f:
            template_bytes = f.read()
        template_reader = PdfReader(io.BytesIO(template_bytes))

        # Create overlay PDF with ReportLab
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        can.setFont("Helvetica", 11)

        # Draw employee data
        can.drawString(330, 470, self.name)
        can.drawString(60, 450, self.voluntar_oras)
        can.drawString(200, 450, self.voluntar_strada)
        can.drawString(320, 450, self.voluntar_numar)
        can.drawString(400, 450, self.voluntar_judet)
        can.drawString(70, 432, self.voluntar_serie_buletin)
        can.drawString(140, 432, self.voluntar_numar_buletin)
        can.drawString(270, 432, self.voluntar_cnp)
        can.drawString(180, 400, "Voluntar")
        can.drawString(
            350, 415,
            f"{self.voluntar_date_from.strftime('%d.%m.%Y')} - {self.voluntar_date_to.strftime('%d.%m.%Y')}"
        )
        can.drawString(420, 217, today_date)

        can.showPage()
        can.save()

        # Merge overlay with template
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        writer = PdfWriter()

        for i, page in enumerate(template_reader.pages):
            if i == 0:  # Only overlay the first page
                page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)

        # Save merged PDF in memory
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        # Encode PDF for attachment
        file_content = base64.b64encode(output_stream.read())

        # Create Odoo attachment
        attachment = self.env['ir.attachment'].create({
            'name': f"Adeverinta_{self.name}.pdf",
            'type': 'binary',
            'datas': file_content,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        # Return URL for download
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{attachment.id}?download=true",
            'target': 'self',
        }
