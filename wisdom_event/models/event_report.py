from odoo import models, api, _, fields
from odoo.exceptions import UserError

class EventReport(models.Model):
    _name = 'event.report'

    name = fields.Char(string="Titlu Raport", required=True)
    worked_hours = fields.Float(string="Ore Lucrate")
    event_id = fields.Many2one('event.event', string="Eveniment", required=True)
    task_description = fields.Text(string="Descriere Sarcini")
    attachments_ids = fields.Many2many('ir.attachment', string="Poze / Documente")
    state = fields.Selection([('draft', 'Draft'), ('sent', 'Trimis')], default='draft', string="Status")


    def action_send_report(self):
        """Demo action for sending the report"""
        for report in self:
            # Change status
            report.state = 'sent'
            
            # Post a message in the related event's chatter
            if report.event_id:
                report.event_id.message_post(
                    body=f"Raport trimis: {report.name}\nOre lucrate: {report.worked_hours}\nDescriere: {report.task_description}"
                )
            
            # Optional: return a notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Raport trimis",
                'message': "Raportul a fost trimis cu succes!",
                'type': 'success',
                'sticky': False,
            }
        }
