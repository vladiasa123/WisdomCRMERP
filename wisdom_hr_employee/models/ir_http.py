from odoo import models, api

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def session_info(self):
        info = super().session_info()

        user = self.env.user
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        info['department_type'] = employee.department_id.name if employee.department_id else False

        # Fetch published events safely
        EventModel = self.env.get('event.event')
        events_list = []
        if EventModel and 'website_published' in EventModel._fields:
            events = EventModel.sudo().search([('website_published', '=', True)], limit=5)
            events_list = [
                {
                    "id": e.id,
                    "name": e.name,
                    "date_begin": str(e.date_begin),
                    "date_end": str(e.date_end),
                }
                for e in events
            ]
        
        info['available_events'] = events_list
        return info
