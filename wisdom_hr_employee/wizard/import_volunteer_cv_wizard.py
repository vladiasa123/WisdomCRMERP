from odoo import models, fields, api, _
import base64
import mimetypes
import logging
import imghdr

_logger = logging.getLogger(__name__)

class ImportVolunteerWizard(models.TransientModel):
    _name = 'res.users.import.wizard'
    _description = 'Import Volunteer Data Wizard'

    file = fields.Binary(string="Upload File", required=True)
    filename = fields.Char(string="File Name")

    def action_import_file(self):
        self.ensure_one()
        active_user = self.env['res.users'].browse(self.env.context.get('active_id'))

        if not self.file:
            raise ValueError(_("Please upload a file."))

        # Decode Base64 file
        file_bytes = base64.b64decode(self.file)

        # Detect MIME type from filename
        if self.filename:
            mime_type, _ = mimetypes.guess_type(self.filename)
        else:
            # detect from content
            image_type = imghdr.what(None, h=file_bytes)
            if image_type == 'png':
                mime_type = 'image/png'
            elif image_type == 'jpeg':
                mime_type = 'image/jpeg'
            elif image_type == 'tiff':
                mime_type = 'image/tiff'
            else:
                mime_type = 'application/pdf'

        # Ensure MIME type is supported by Document AI
        supported_types = ["application/pdf", "image/png", "image/jpeg", "image/tiff"]
        if mime_type not in supported_types:
            raise ValueError(_("Unsupported file type: %s") % mime_type)

        _logger.info(
            "Uploading file %s (MIME: %s, %d bytes)",
            self.filename, mime_type, len(file_bytes)
        )

        # Send file to Document AI processor
        try:
            extracted = active_user.process_document_sample(
                project_id="779079627865",
                location="eu",
                processor_id="8489c250270ac26c",
                file_blob=file_bytes,
                mime_type=mime_type,
            )
            _logger.info("Document AI extracted fields: %s", extracted)
        except Exception as e:
            _logger.exception("Document AI processing failed: %s", e)
            raise

        return {'type': 'ir.actions.act_window_close'}
