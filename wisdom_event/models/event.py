from odoo import models, api, _, fields
from odoo.exceptions import UserError

class EventEvent(models.Model):
    _inherit = 'event.event'

    def action_enroll_user(self):
        self.env['event.registration'].create({
            'event_id': self.id,
            'partner_id': self.env.user.partner_id.id,
        })
        return True

 
    def action_attend_event(self):
        """Register the current user as attendee of this event
        and add it to their calendar, if no overlap."""
        Attendee = self.env['event.registration']
        Calendar = self.env['calendar.event']
        current_user = self.env.user
        current_partner = current_user.partner_id

        for event in self:
            # 1. Check if already registered
            already = Attendee.search([
                ('event_id', '=', event.id),
                ('partner_id', '=', current_partner.id)
            ], limit=1)
            if already:
                raise UserError(_("You are already attending this event."))

            # 2. Check for overlapping events
            overlapping = Attendee.search([
                ('partner_id', '=', current_partner.id),
                ('event_id.date_begin', '<', event.date_end),
                ('event_id.date_end', '>', event.date_begin),
            ], limit=1)
            if overlapping:
                raise UserError(_(
                    "You are already attending another event (%s) during this time."
                ) % overlapping.event_id.display_name)

            # 3. Register as attendee
            Attendee.create({
                'event_id': event.id,
                'partner_id': current_partner.id,
                'name': current_partner.name,
                'email': current_partner.email,
            })

            # 4. Add to user's calendar
            Calendar.create({
                'name': event.name,
                'start': event.date_begin,
                'stop': event.date_end,
                'allday': False,
                'user_id': current_user.id,
                'partner_ids': [(4, current_partner.id)],
                'description': event.description or '',
            })

        return True