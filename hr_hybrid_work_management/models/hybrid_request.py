from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class HrHybridRequest(models.Model):
    _name = 'hr.hybrid.request'
    _description = 'Hybrid Work and Work From Home Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Request Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        tracking=True,
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )

    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        compute='_compute_manager_id',
        store=True,
        readonly=False,
        tracking=True,
    )

    work_mode = fields.Selection(
        [
            ('wfh', 'Work From Home'),
            ('hybrid', 'Hybrid Work'),
        ],
        string='Work Mode',
        required=True,
        default='wfh',
        tracking=True,
    )

    date_from = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
    )

    date_to = fields.Date(
        string='End Date',
        required=True,
        tracking=True,
    )

    requested_days = fields.Integer(
        string='Requested Days',
        compute='_compute_requested_days',
        store=True,
    )

    monthly_wfh_limit = fields.Integer(
        string='Monthly WFH Limit',
        default=8,
        readonly=True,
    )

    used_wfh_days = fields.Integer(
        string='Used WFH Days This Month',
        compute='_compute_wfh_balance',
    )

    remaining_wfh_days = fields.Integer(
        string='Remaining WFH Days This Month',
        compute='_compute_wfh_balance',
    )

    reason = fields.Text(
        string='Reason',
        required=True,
    )

    daily_report = fields.Text(
        string='Daily Work Report',
        help='Employee reports completed work during WFH/Hybrid day.',
        tracking=True,
    )

    manager_note = fields.Text(
        string='Manager Comment',
        tracking=True,
    )

    attendance_id = fields.Many2one(
        'hr.attendance',
        string='Attendance Record',
        readonly=True,
    )

    check_in_time = fields.Datetime(
        string='Check In',
        readonly=True,
        tracking=True,
    )

    check_out_time = fields.Datetime(
        string='Check Out',
        readonly=True,
        tracking=True,
    )

    worked_hours = fields.Float(
        string='Worked Hours',
        compute='_compute_worked_hours',
        store=True,
    )

    attendance_status = fields.Selection(
        [
            ('not_started', 'Not Started'),
            ('checked_in', 'Checked In'),
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('adjusted', 'Adjusted'),
        ],
        string='Attendance Status',
        default='not_started',
        tracking=True,
    )

    adjustment_reason = fields.Text(
        string='Adjustment Reason',
        tracking=True,
    )

    can_hr_approve_attendance = fields.Boolean(
        string='Can HR Approve Attendance',
        compute='_compute_can_hr_approve_attendance',
    )

    can_manager_approve = fields.Boolean(
        string='Can Manager Approve',
        compute='_compute_can_manager_approve',
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )

    @api.depends('employee_id')
    def _compute_manager_id(self):
        for rec in self:
            rec.manager_id = rec.employee_id.parent_id if rec.employee_id else False

    @api.depends('manager_id')
    def _compute_can_manager_approve(self):
        for rec in self:
            rec.can_manager_approve = bool(
                rec.manager_id
                and rec.manager_id.user_id
                and rec.manager_id.user_id == self.env.user
            )

    @api.depends('check_in_time', 'check_out_time')
    def _compute_worked_hours(self):
        for rec in self:
            if rec.check_in_time and rec.check_out_time:
                delta = rec.check_out_time - rec.check_in_time
                rec.worked_hours = delta.total_seconds() / 3600
            else:
                rec.worked_hours = 0

    def _compute_can_hr_approve_attendance(self):
        for rec in self:
            rec.can_hr_approve_attendance = self.env.user.has_group(
                'hr_hybrid_work_management.group_hr_hybrid_hr'
            )

    @api.depends('date_from', 'date_to')
    def _compute_requested_days(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                rec.requested_days = (rec.date_to - rec.date_from).days + 1
            else:
                rec.requested_days = 0

    def _compute_wfh_balance(self):
        for rec in self:
            used_days = 0

            if rec.employee_id and rec.date_from:
                month_start = rec.date_from.replace(day=1)

                if rec.date_from.month == 12:
                    month_end = rec.date_from.replace(
                        year=rec.date_from.year + 1,
                        month=1,
                        day=1
                    ) - timedelta(days=1)
                else:
                    month_end = rec.date_from.replace(
                        month=rec.date_from.month + 1,
                        day=1
                    ) - timedelta(days=1)

                approved_requests = self.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'approved'),
                    ('date_from', '>=', month_start),
                    ('date_to', '<=', month_end),
                    ('id', '!=', rec.id),
                ])

                used_days = sum(approved_requests.mapped('requested_days'))

            rec.used_wfh_days = used_days
            rec.remaining_wfh_days = max(
                rec.monthly_wfh_limit - used_days - rec.requested_days,
                0
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hr.hybrid.request'
                ) or 'New'
        return super().create(vals_list)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(
                    _('Start Date must be before or equal to End Date.')
                )

    def _get_employee_email(self):
        self.ensure_one()
        return (
            self.employee_id.work_email
            or self.employee_id.user_id.email
            or self.employee_id.private_email
        )

    def _send_result_email(self, result):
        for rec in self:
            employee_email = rec._get_employee_email()

            if not employee_email:
                rec.message_post(
                    body=_(
                        'Cannot send email because the employee does not have an email address.'
                    )
                )
                continue

            work_mode_label = dict(rec._fields['work_mode'].selection).get(
                rec.work_mode,
                rec.work_mode,
            )

            subject = _('Hybrid/WFH Request %s - %s') % (result, rec.name)

            body_html = """
                <p>Dear %s,</p>
                <p>Your Hybrid/WFH request <b>%s</b> has been <b>%s</b>.</p>
                <p><b>Work Mode:</b> %s</p>
                <p><b>Start Date:</b> %s</p>
                <p><b>End Date:</b> %s</p>
                <p><b>Manager:</b> %s</p>
                <p><b>Manager Comment:</b> %s</p>
                <p>Thank you.</p>
            """ % (
                rec.employee_id.name or '',
                rec.name or '',
                result,
                work_mode_label or '',
                rec.date_from or '',
                rec.date_to or '',
                rec.manager_id.name or '',
                rec.manager_note or '',
            )

            self.env['mail.mail'].sudo().create({
                'subject': subject,
                'body_html': body_html,
                'email_to': employee_email,
                'auto_delete': False,
                'model': rec._name,
                'res_id': rec.id,
            }).send()

            rec.message_post(
                body=_('Result email has been sent to %s.') % employee_email
            )

    def action_submit(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft requests can be submitted.'))

            if rec.requested_days > rec.remaining_wfh_days:
                raise UserError(
                    _('Requested days exceed remaining WFH days this month.')
                )

            rec.state = 'submitted'

            rec.message_post(
                body=_('The request has been submitted to the manager.')
            )

            if rec.manager_id and rec.manager_id.user_id:
                rec.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=rec.manager_id.user_id.id,
                    summary=_('Review Hybrid/WFH Request'),
                    note=_('Please review this Hybrid/WFH request.'),
                )

    def action_approve(self):
        for rec in self:
            if not rec.can_manager_approve:
                raise UserError(
                    _('Only the assigned manager can approve this request.')
                )

            if rec.state != 'submitted':
                raise UserError(_('Only submitted requests can be approved.'))

            rec.state = 'approved'

            if not rec.manager_note:
                rec.manager_note = _('Approved by Manager.')

            rec.activity_unlink(['mail.mail_activity_data_todo'])

            rec.message_post(
                body=_('The request has been approved by the manager.')
            )

            rec._send_result_email(_('Approved'))

    def action_reject(self):
        for rec in self:
            if not rec.can_manager_approve:
                raise UserError(
                    _('Only the assigned manager can reject this request.')
                )

            if rec.state != 'submitted':
                raise UserError(_('Only submitted requests can be rejected.'))

            rec.state = 'rejected'

            if not rec.manager_note:
                rec.manager_note = _('Rejected by Manager.')

            rec.activity_unlink(['mail.mail_activity_data_todo'])

            rec.message_post(
                body=_('The request has been rejected by the manager.')
            )

            rec._send_result_email(_('Rejected'))

    def action_cancel(self):
        for rec in self:
            if rec.state in ('approved', 'rejected'):
                raise UserError(
                    _('Approved or rejected requests cannot be cancelled.')
                )

            rec.state = 'cancelled'

            rec.message_post(
                body=_('The request has been cancelled.')
            )

    def action_reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'

            rec.message_post(
                body=_('The request has been reset to draft.')
            )

    def action_check_in(self):
        for rec in self:
            if rec.employee_id.user_id != self.env.user:
                raise UserError(
                    _('Only the employee can check in.')
                )

            if rec.state != 'approved':
                raise UserError(
                    _('Only approved requests can be checked in.')
                )

            if rec.check_in_time:
                raise UserError(_('You have already checked in.'))

            now = fields.Datetime.now()

            attendance = self.env['hr.attendance'].create({
                'employee_id': rec.employee_id.id,
                'check_in': now,
            })

            rec.attendance_id = attendance.id
            rec.check_in_time = now
            rec.attendance_status = 'checked_in'

            rec.message_post(
                body=_('Employee checked in for Hybrid/WFH work.')
            )

    def action_check_out(self):
        for rec in self:
            if rec.employee_id.user_id != self.env.user:
                raise UserError(
                    _('Only the employee can check out.')
                )

            if not rec.check_in_time:
                raise UserError(_('You must check in before checking out.'))

            if rec.check_out_time:
                raise UserError(_('You have already checked out.'))

            now = fields.Datetime.now()

            if rec.attendance_id:
                rec.attendance_id.write({
                    'check_out': now,
                })

            rec.check_out_time = now
            rec.attendance_status = 'pending'

            rec.message_post(
                body=_('Employee checked out for Hybrid/WFH work.')
            )

    def action_approve_attendance(self):
        for rec in self:
            if not self.env.user.has_group(
                'hr_hybrid_work_management.group_hr_hybrid_hr'
            ):
                raise UserError(_('Only HR Officer can approve attendance.'))

            if rec.attendance_status not in ('pending', 'adjusted'):
                raise UserError(
                    _('Only pending or adjusted attendance can be approved.')
                )

            rec.attendance_status = 'approved'

            rec.message_post(
                body=_('Attendance has been approved by HR.')
            )

    def action_adjust_attendance(self):
        for rec in self:
            if not self.env.user.has_group(
                'hr_hybrid_work_management.group_hr_hybrid_hr'
            ):
                raise UserError(_('Only HR Officer can adjust attendance.'))

            if not rec.check_in_time or not rec.check_out_time:
                raise UserError(
                    _('Check In and Check Out time are required before adjustment.')
                )

            if rec.check_in_time > rec.check_out_time:
                raise UserError(
                    _('Check In time must be before Check Out time.')
                )

            if rec.attendance_id:
                rec.attendance_id.write({
                    'check_in': rec.check_in_time,
                    'check_out': rec.check_out_time,
                })

            rec.attendance_status = 'adjusted'

            rec.message_post(
                body=_('Attendance has been adjusted by HR. Reason: %s')
                % (rec.adjustment_reason or _('No reason provided.'))
            )