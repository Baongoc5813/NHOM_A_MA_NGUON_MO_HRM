# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class InterviewScheduleWizard(models.TransientModel):
    _name = 'interview.schedule.wizard'
    _description = 'Smart Interview Scheduling Wizard'

    applicant_id = fields.Many2one(
        'hr.applicant', string='Applicant', required=True, readonly=True,
    )
    candidate_name = fields.Char(
        related='applicant_id.partner_name', string='Candidate', readonly=True,
    )
    job_id = fields.Many2one(
        related='applicant_id.job_id', string='Position', readonly=True,
    )
    interview_round = fields.Selection([
        ('1', 'Round 1 - HR Screening'),
        ('2', 'Round 2 - Technical'),
        ('3', 'Round 3 - Culture Fit'),
        ('4', 'Round 4 - Final'),
    ], string='Interview Round', required=True, default='1')

    interview_type = fields.Selection([
        ('online', 'Online'),
        ('onsite', 'On-site'),
        ('phone',  'Phone'),
    ], string='Interview Type', required=True, default='online')

    meeting_url  = fields.Char(string='Meeting URL')
    location     = fields.Char(string='Location / Room')
    duration     = fields.Float(string='Duration (hours)', default=1.0)

    interviewer_ids = fields.Many2many(
        'res.users', string='Interviewers', required=True,
    )
    date_from = fields.Datetime(
        string='Search From',
        default=lambda self: fields.Datetime.now(),
        required=True,
    )
    date_to = fields.Datetime(
        string='Search Until',
        default=lambda self: fields.Datetime.now() + timedelta(days=7),
        required=True,
    )
    available_slot_ids = fields.One2many(
        'interview.schedule.wizard.slot', 'wizard_id',
        string='Available Slots',
    )
    selected_start = fields.Datetime(string='Selected Start')
    selected_stop  = fields.Datetime(string='Selected End')

    def action_find_slots(self):
        self.ensure_one()
        if not self.interviewer_ids:
            raise UserError(_('Please select at least one interviewer.'))
        duration_minutes = int(self.duration * 60)
        slots = self.env['calendar.event'].get_interviewer_free_slots(
            self.interviewer_ids.ids,
            self.date_from,
            self.date_to,
            duration_minutes=duration_minutes,
        )
        self.available_slot_ids.unlink()
        if not slots:
            raise UserError(_(
                'No free slots found. Please expand the search window '
                'or choose different interviewers.'
            ))
        self.env['interview.schedule.wizard.slot'].create([
            {
                'wizard_id': self.id,
                'start':     s['start'],
                'stop':      s['end'],
                'label':     s['label'],
            }
            for s in slots[:20]
        ])
        return {
            'type':      'ir.actions.act_window',
            'res_model': 'interview.schedule.wizard',
            'res_id':    self.id,
            'view_mode': 'form',
            'target':    'new',
        }

    def action_confirm_schedule(self):
        self.ensure_one()
        if not self.selected_start or not self.selected_stop:
            raise UserError(_('Please select a time slot before confirming.'))

        round_labels = dict(self._fields['interview_round'].selection)
        round_label  = round_labels.get(self.interview_round, '')
        event_name   = 'Interview: %s - %s' % (self.candidate_name, round_label)

        candidate_partner    = self.applicant_id.partner_id
        interviewer_partners = self.interviewer_ids.mapped('partner_id')
        all_partners         = candidate_partner | interviewer_partners

        lines = ['Interview for %s' % self.candidate_name]
        if self.job_id:
            lines.append('Position: %s' % self.job_id.name)
        lines.append('Type: %s' % self.interview_type)
        if self.meeting_url:
            lines.append('Meeting URL: %s' % self.meeting_url)

        event = self.env['calendar.event'].create({
            'name':                 event_name,
            'start':                self.selected_start,
            'stop':                 self.selected_stop,
            'is_interview':         True,
            'applicant_id':         self.applicant_id.id,
            'interview_round':      self.interview_round,
            'interview_type':       self.interview_type,
            'interview_meeting_url': self.meeting_url,
            'location':             self.location,
            'partner_ids':          [(6, 0, all_partners.ids)],
            'description':          '\n'.join(lines),
        })
        event.action_send_interview_invitations()
        return {
            'type':      'ir.actions.act_window',
            'name':      _('Interview Event'),
            'res_model': 'calendar.event',
            'res_id':    event.id,
            'view_mode': 'form',
            'target':    'current',
        }


class InterviewScheduleWizardSlot(models.TransientModel):
    _name = 'interview.schedule.wizard.slot'
    _description = 'Available Interview Time Slot'
    _order = 'start asc'

    wizard_id = fields.Many2one('interview.schedule.wizard', ondelete='cascade')
    start = fields.Datetime(string='Start')
    stop  = fields.Datetime(string='End')
    label = fields.Char(string='Slot Label')

    def action_select_slot(self):
        self.ensure_one()
        self.wizard_id.write({
            'selected_start': self.start,
            'selected_stop':  self.stop,
        })
        return {
            'type':      'ir.actions.act_window',
            'res_model': 'interview.schedule.wizard',
            'res_id':    self.wizard_id.id,
            'view_mode': 'form',
            'target':    'new',
        }
