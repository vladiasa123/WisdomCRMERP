from odoo import models, api

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def session_info(self):
        info = super().session_info()

        user = self.env.user
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)

        info['department_type'] = employee.department_id.name if employee.department_id else False

        # Fetch published events
        events = self.env['event.event'].sudo().search([('is_published', '=', True)], limit=5)
        info['available_events'] = [
            {"id": e.id, "name": e.name, "date_begin": str(e.date_begin), "date_end": str(e.date_end)}
            for e in events
        ]
        return info
