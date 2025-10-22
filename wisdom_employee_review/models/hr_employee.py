from odoo import models, fields, api
from odoo.exceptions import UserError
import os
import json
import io
import base64
from datetime import datetime

from openai import OpenAI
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

class HrEmployee(models.Model):
    _inherit = 'hr.employee'




    def action_download_adeverinta_pdf(self):
        """Fill adeverinta PDF with employee data and return download"""
        self.ensure_one()
        today_date = datetime.today().strftime("%d.%m.%Y")  # Format as dd.mm.yyyy


        # Path to your uploaded PDF template (place it in your module's /static/src/pdf/)
        template_path = "/home/vladiasa/testWisdom/odoo-18.0.post20250801/custom/wisdom_employee_review/data/Adeverinta voluntariat Procivitas.pdf"

        # Read PDF template
        template_reader = PdfReader(open(template_path, "rb"))
        packet = io.BytesIO()


        can = canvas.Canvas(packet, pagesize=A4)


        can.setFont("Helvetica", 11)
        can.drawString(330, 470, self.name or "")                  
        can.drawString(60, 450, self.voluntar_oras)        
        can.drawString(200, 450, self.voluntar_strada) 
        can.drawString(320, 450, self.voluntar_numar)       
        can.drawString(400, 450, self.voluntar_judet)  
        can.drawString(70, 432, self.voluntar_serie_buletin)   
        can.drawString(140, 432, self.voluntar_numar_buletin)          
        can.drawString(270, 432, self.voluntar_cnp or "50122011001")                
        can.drawString(180, 400, "Voluntar")    
        can.drawString(350, 415, f"{self.voluntar_date_from.strftime('%d.%m.%Y')} - {self.voluntar_date_to.strftime('%d.%m.%Y')}")
        can.drawString(420, 217, today_date)               

        can.showPage()
        can.save()

        # Merge overlay with template
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        writer = PdfWriter()

        for i in range(len(template_reader.pages)):
            page = template_reader.pages[i]
            if i == 0:  # only overlay on first page
                page.merge_page(overlay_pdf.pages[0])
            writer.add_page(page)

        # Save result
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        # Encode in base64
        file_content = base64.b64encode(output_stream.read())

        # Create attachment to return
        attachment = self.env['ir.attachment'].create({
            'name': f"Adeverinta_{self.name}.pdf",
            'type': 'binary',
            'datas': file_content,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf'
        })

        # Return file for download
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{attachment.id}?download=true",
            'target': 'self',
        }