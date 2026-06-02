# -*- coding: utf-8 -*-
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    is_interview = fields.Boolean(string='Is Interview', default=False, index=True)
    applicant_id = fields.Many2one(
        'hr.applicant', string='Applicant', ondelete='cascade', index=True,
    )
    interview_round = fields.Selection([
        ('1', 'Round 1 - HR Screening'),
        ('2', 'Round 2 - Technical'),
        ('3', 'Round 3 - Culture Fit'),
        ('4', 'Round 4 - Final'),
    ], string='Interview Round')

    interview_type = fields.Selection([
        ('online', 'Online'),
        ('onsite', 'On-site'),
        ('phone',  'Phone'),
    ], string='Interview Type', default='online')

    interview_meeting_url = fields.Char(string='Interview Meeting URL')

    candidate_attendance = fields.Selection([
        ('pending',     'Pending'),
        ('showed_up',   'Showed Up'),
        ('no_show',     'No Show'),
        ('rescheduled', 'Rescheduled'),
        ('cancelled',   'Cancelled'),
    ], string='Candidate Attendance', default='pending')

    interview_feedback_ids = fields.One2many(
        'hr.interview.feedback', 'calendar_event_id',
        string='Interview Feedbacks',
    )
    interview_feedback_count = fields.Integer(
        string='Feedback Count',
        compute='_compute_interview_feedback_count', store=True,
    )

    @api.depends('interview_feedback_ids')
    def _compute_interview_feedback_count(self):
        for rec in self:
            rec.interview_feedback_count = len(rec.interview_feedback_ids)

    def action_send_interview_invitations(self):
        self.ensure_one()
        if not self.is_interview:
            raise UserError(_('This is not an interview event.'))
        template = self.env.ref(
            'interview_scheduling.email_template_interview_invitation',
            raise_if_not_found=False,
        )
        if template:
            template.send_mail(self.id, force_send=True)
        for partner in self.partner_ids:
            user = partner.user_ids[:1]
            if not user:
                continue
            if not self.interview_feedback_ids.filtered(
                lambda f: f.interviewer_id == user
            ):
                self.env['hr.interview.feedback'].create({
                    'applicant_id':      self.applicant_id.id,
                    'calendar_event_id': self.id,
                    'interviewer_id':    user.id,
                    'interview_round':   self.interview_round or '1',
                    'interview_type':    self.interview_type or 'online',
                })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title':   _('Invitations Sent'),
                'message': _('Interview invitations sent to all participants.'),
                'sticky':  False,
                'type':    'success',
            },
        }

    # Separate methods for each attendance status (no parameters)
    def action_mark_showed_up(self):
        self.ensure_one()
        self.candidate_attendance = 'showed_up'
        if self.applicant_id:
            self.applicant_id.last_interview_attendance = 'showed_up'

    def action_mark_no_show(self):
        self.ensure_one()
        self.candidate_attendance = 'no_show'
        if self.applicant_id:
            self.applicant_id.last_interview_attendance = 'no_show'

    def action_mark_rescheduled(self):
        self.ensure_one()
        self.candidate_attendance = 'rescheduled'
        if self.applicant_id:
            self.applicant_id.last_interview_attendance = 'rescheduled'

    def action_open_interview_feedbacks(self):
        self.ensure_one()
        return {
            'type':      'ir.actions.act_window',
            'name':      _('Interview Feedbacks'),
            'res_model': 'hr.interview.feedback',
            'view_mode': 'list,form',
            'domain':    [('calendar_event_id', '=', self.id)],
            'context':   {
                'default_calendar_event_id': self.id,
                'default_applicant_id':      self.applicant_id.id,
            },
        }

    @api.model
    def get_interviewer_free_slots(self, interviewer_ids, date_from, date_to,
                                   duration_minutes=60):
        slot_duration = timedelta(minutes=duration_minutes)
        current = date_from
        free_slots = []
        partners = self.env['res.users'].browse(interviewer_ids).mapped('partner_id')
        busy_events = self.search([
            ('partner_ids', 'in', partners.ids),
            ('start', '<', date_to),
            ('stop',  '>', date_from),
        ])
        while current + slot_duration <= date_to:
            slot_end = current + slot_duration
            conflict = busy_events.filtered(
                lambda e: e.start < slot_end and e.stop > current
            )
            if not conflict:
                free_slots.append({
                    'start': current,
                    'end':   slot_end,
                    'label': current.strftime('%A, %d %b %Y - %H:%M'),
                })
            current += timedelta(minutes=30)
        return free_slots
