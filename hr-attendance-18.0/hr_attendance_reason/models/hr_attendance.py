from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import pytz


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_reason_ids = fields.Many2many(
        comodel_name="hr.attendance.reason",
        string="Attendance Reason",
        help="Specifies the reason for signing In/signing Out in case of "
             "less or extra hours.",
    )

    attendance_type = fields.Selection(
        selection=[
            ('attendance', 'Attendance'),
            ('event', 'Event'),
        ],       string='Attendance Type',
        default='attendance',   required=True, tracking=True        

    )

    event_pictures = fields.Many2many(
        'ir.attachment',
        'attendance_event_image_rel',   # relation table
        'attendance_id', 'attachment_id',
        string="Event Pictures",
        help="Upload one or more pictures for the event attendance."
    )

    event_documents = fields.Many2many(
        'ir.attachment',
        'attendance_event_document_rel',  # relation table for docs
        'attendance_id', 'attachment_id',
        string="Event Documents",
        help="Upload one or more documents (PDF, DOCX, etc.) for the event attendance."
    )

    event_description = fields.Text(
        string="Event Description",
        help="Optional description or notes about this event attendance."
    )


    event_id = fields.Many2one(
        'event.event',
        string="Event",
        domain="[('id', 'in', available_event_ids)]"
    )

    available_event_ids = fields.Many2many(
        'event.event',
        compute='_compute_available_event_ids',
        string='Available Events',
        store=False,
    )

    @api.depends('employee_id')
    def _compute_available_event_ids(self):
        """Restrict events to those the employee is attending"""
        for rec in self:
            if rec.employee_id:
                rec.available_event_ids = self.env['event.event'].search([
                    ('registration_ids.partner_id',
                     '=',
                     rec.employee_id.user_id.partner_id.id)
                ])
            else:
                rec.available_event_ids = self.env['event.event']

    # proxy time-only fields for the UI
    time_in = fields.Float(string="Check In", compute="_compute_time_in",
                           inverse="_inverse_time_in", store=False)
    time_out = fields.Float(string="Check Out", compute="_compute_time_out",
                            inverse="_inverse_time_out", store=False)

    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now,
                               required=True, tracking=True)
    check_out = fields.Datetime(string="Check Out", tracking=True)

    # ---- helpers
    def _float_from_dt(self, dt):
        if not dt:
            return 0.0
        local = fields.Datetime.context_timestamp(self, dt)
        return local.hour + local.minute / 60.0

    def _dt_from_float_today(self, hours_float):
        tzname = self.env.context.get("tz") or self.env.user.tz or "UTC"
        tz = pytz.timezone(tzname)
        now_local = datetime.now(tz)
        hh = int(hours_float)
        mm = int(round((hours_float - hh) * 60))
        local_dt = now_local.replace(hour=hh, minute=mm, second=0, microsecond=0)
        return local_dt.astimezone(pytz.UTC).replace(tzinfo=None)

    # ---- computes
    @api.depends('check_in')
    def _compute_time_in(self):
        for rec in self:
            rec.time_in = rec._float_from_dt(rec.check_in) if rec.check_in else 0.0

    @api.depends('check_out')
    def _compute_time_out(self):
        for rec in self:
            rec.time_out = rec._float_from_dt(rec.check_out) if rec.check_out else 0.0

    # ---- inverses
    def _inverse_time_in(self):
        for rec in self:
            rec.check_in = rec._dt_from_float_today(rec.time_in) if rec.time_in is not None else False

    def _inverse_time_out(self):
        for rec in self:
            rec.check_out = rec._dt_from_float_today(rec.time_out) if rec.time_out is not None else False

    # ---- override write to block approvals
    def write(self, vals):
        if 'overtime_status' in vals:  
            if not self.env.user.has_group('hr_attendance.group_hr_attendance_manager'):
                raise UserError(_("You are not allowed to approve your own attendance. Please ask a manager."))
        return super().write(vals)

    def create(self, vals_list):
        return super().create(vals_list)
