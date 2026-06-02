# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrInterviewFeedback(models.Model):
    _name = 'hr.interview.feedback'
    _description = 'Interview Feedback'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    applicant_id = fields.Many2one(
        'hr.applicant', string='Applicant',
        required=True, ondelete='cascade', index=True, tracking=True,
    )
    calendar_event_id = fields.Many2one(
        'calendar.event', string='Interview Event', ondelete='set null',
    )
    interviewer_id = fields.Many2one(
        'res.users', string='Interviewer',
        required=True, default=lambda self: self.env.user, tracking=True,
    )
    job_id = fields.Many2one(
        'hr.job', string='Applied Job',
        related='applicant_id.job_id', store=True, readonly=True,
    )
    interview_date = fields.Datetime(
        string='Interview Date',
        related='calendar_event_id.start', store=True, readonly=True,
    )
    interview_round = fields.Selection([
        ('1', 'Round 1 - HR Screening'),
        ('2', 'Round 2 - Technical'),
        ('3', 'Round 3 - Culture Fit'),
        ('4', 'Round 4 - Final'),
    ], string='Round', default='1', required=True, tracking=True)

    interview_type = fields.Selection([
        ('online', 'Online'),
        ('onsite', 'On-site'),
        ('phone',  'Phone'),
    ], string='Type', default='online', required=True)

    attendance_status = fields.Selection([
        ('pending',     'Pending'),
        ('showed_up',   'Showed Up'),
        ('no_show',     'No Show'),
        ('rescheduled', 'Rescheduled'),
        ('cancelled',   'Cancelled'),
    ], string='Attendance', default='pending', required=True, tracking=True)

    score_communication   = fields.Integer(string='Communication (0-10)',   default=0)
    score_technical       = fields.Integer(string='Technical (0-10)',       default=0)
    score_problem_solving = fields.Integer(string='Problem Solving (0-10)', default=0)
    score_culture_fit     = fields.Integer(string='Culture Fit (0-10)',     default=0)
    score_overall         = fields.Float(
        string='Overall Score',
        compute='_compute_overall_score', store=True,
    )

    strengths  = fields.Text(string='Strengths', tracking=True)
    weaknesses = fields.Text(string='Areas for Improvement', tracking=True)
    notes      = fields.Text(string='Additional Notes')

    recommendation = fields.Selection([
        ('pass',     'Pass'),
        ('fail',     'Fail'),
        ('consider', 'Consider'),
        ('hold',     'On Hold'),
    ], string='Recommendation', tracking=True)

    state = fields.Selection([
        ('draft',     'Draft'),
        ('submitted', 'Submitted'),
    ], string='Status', default='draft', tracking=True)

    submitted_on = fields.Datetime(string='Submitted On', readonly=True)

    @api.constrains(
        'score_communication', 'score_technical',
        'score_problem_solving', 'score_culture_fit',
    )
    def _check_scores(self):
        for rec in self:
            for fname in (
                'score_communication', 'score_technical',
                'score_problem_solving', 'score_culture_fit',
            ):
                if not (0 <= getattr(rec, fname) <= 10):
                    raise ValidationError(_('Scores must be between 0 and 10.'))

    @api.depends(
        'score_communication', 'score_technical',
        'score_problem_solving', 'score_culture_fit',
    )
    def _compute_overall_score(self):
        for rec in self:
            scores = [
                rec.score_communication, rec.score_technical,
                rec.score_problem_solving, rec.score_culture_fit,
            ]
            filled = [s for s in scores if s > 0]
            rec.score_overall = sum(filled) / len(filled) if filled else 0.0

    def action_submit_feedback(self):
        for rec in self:
            if not rec.recommendation:
                raise ValidationError(
                    _('Please select a Recommendation before submitting.')
                )
            rec.write({
                'state': 'submitted',
                'submitted_on': fields.Datetime.now(),
            })
            rec.applicant_id._recompute_interview_summary()
        return True

    def action_reset_to_draft(self):
        self.write({'state': 'draft', 'submitted_on': False})
