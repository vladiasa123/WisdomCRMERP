from odoo import models, fields, api, _
import base64
import tempfile
import mimetypes
import logging

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

        # Decode to bytes
        file_bytes = base64.b64decode(self.file)

        # Detect MIME type from filename
        mime_type, _ = mimetypes.guess_type(self.filename or "")
        if not mime_type:
            # Default to PDF if undetectable
            mime_type = "application/pdf"

        _logger.info("Uploading file %s (MIME: %s, %d bytes)",
                    self.filename, mime_type, len(file_bytes))

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