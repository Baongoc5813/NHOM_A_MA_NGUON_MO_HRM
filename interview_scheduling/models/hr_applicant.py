# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    interview_event_ids = fields.One2many(
        'calendar.event', 'applicant_id', string='Interview Events',
    )
    interview_count = fields.Integer(
        string='Interviews', compute='_compute_interview_count', store=True,
    )
    interview_feedback_ids = fields.One2many(
        'hr.interview.feedback', 'applicant_id', string='Interview Feedbacks',
    )
    interview_feedback_count = fields.Integer(
        string='Feedbacks', compute='_compute_feedback_count', store=True,
    )
    last_interview_date = fields.Datetime(
        string='Last Interview',
        compute='_compute_interview_summary', store=True,
    )
    last_interview_attendance = fields.Selection([
        ('pending',     'Pending'),
        ('showed_up',   'Showed Up'),
        ('no_show',     'No Show'),
        ('rescheduled', 'Rescheduled'),
        ('cancelled',   'Cancelled'),
    ], string='Last Attendance', tracking=True)

    overall_recommendation = fields.Selection([
        ('pass',    'Pass'),
        ('fail',    'Fail'),
        ('consider','Consider'),
        ('hold',    'On Hold'),
        ('pending', 'Pending Feedback'),
    ], string='Overall Recommendation',
       compute='_compute_interview_summary', store=True,
    )
    average_score = fields.Float(
        string='Avg. Score',
        compute='_compute_interview_summary', store=True, digits=(4, 2),
    )

    @api.depends('interview_event_ids', 'interview_event_ids.is_interview')
    def _compute_interview_count(self):
        for rec in self:
            rec.interview_count = len(
                rec.interview_event_ids.filtered(lambda e: e.is_interview)
            )

    @api.depends('interview_feedback_ids')
    def _compute_feedback_count(self):
        for rec in self:
            rec.interview_feedback_count = len(rec.interview_feedback_ids)

    @api.depends(
        'interview_feedback_ids', 'interview_feedback_ids.state',
        'interview_feedback_ids.score_overall',
        'interview_feedback_ids.recommendation',
        'interview_event_ids', 'interview_event_ids.start',
    )
    def _compute_interview_summary(self):
        for rec in self:
            dates = rec.interview_event_ids.mapped('start')
            rec.last_interview_date = max(dates) if dates else False
            submitted = rec.interview_feedback_ids.filtered(
                lambda f: f.state == 'submitted'
            )
            if not submitted:
                rec.average_score = 0.0
                rec.overall_recommendation = 'pending'
                continue
            scores = submitted.mapped('score_overall')
            rec.average_score = sum(scores) / len(scores) if scores else 0.0
            recs = submitted.mapped('recommendation')
            for verdict in ('fail', 'consider', 'hold', 'pass'):
                if recs.count(verdict) >= len(recs) / 2:
                    rec.overall_recommendation = verdict
                    break
            else:
                rec.overall_recommendation = 'pending'

    def _recompute_interview_summary(self):
        self._compute_interview_summary()

    def action_open_interviews(self):
        self.ensure_one()
        return {
            'type':      'ir.actions.act_window',
            'name':      _('Interview Schedule'),
            'res_model': 'calendar.event',
            'view_mode': 'list,form',
            'domain':    [
                ('applicant_id', '=', self.id),
                ('is_interview', '=', True),
            ],
            'context': {
                'default_applicant_id': self.id,
                'default_is_interview': True,
            },
        }

    def action_open_feedbacks(self):
        self.ensure_one()
        return {
            'type':      'ir.actions.act_window',
            'name':      _('Interview Feedbacks'),
            'res_model': 'hr.interview.feedback',
            'view_mode': 'list,form',
            'domain':    [('applicant_id', '=', self.id)],
            'context':   {'default_applicant_id': self.id},
        }

    def action_schedule_interview(self):
        self.ensure_one()
        return {
            'type':      'ir.actions.act_window',
            'name':      _('Schedule Interview'),
            'res_model': 'interview.schedule.wizard',
            'view_mode': 'form',
            'target':    'new',
            'context':   {'default_applicant_id': self.id},
        }
