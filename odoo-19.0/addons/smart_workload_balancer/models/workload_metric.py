from odoo import models, fields, api
from datetime import date, timedelta


class ProjectWorkloadMetric(models.Model):
    _name = 'project.workload.metric'
    _description = 'Employee Workload Metric'
    _rec_name = 'employee_id'
    _order = 'workload_score desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade', index=True)
    user_id = fields.Many2one(related='employee_id.user_id', string='User', store=True)
    project_id = fields.Many2one('project.project', string='Project', index=True)
    active_tasks_count = fields.Integer(string='Active Tasks', compute='_compute_task_metrics', store=True)
    overdue_tasks_count = fields.Integer(string='Overdue Tasks', compute='_compute_task_metrics', store=True)
    completed_tasks_count = fields.Integer(string='Completed Tasks', compute='_compute_task_metrics', store=True)
    total_timesheet_hours = fields.Float(string='Total Worked Hours', compute='_compute_timesheet_metrics', store=True)
    overtime_hours = fields.Float(string='Overtime Hours', compute='_compute_timesheet_metrics', store=True)
    workload_score = fields.Float(string='Workload Score', compute='_compute_workload_score', store=True)
    workload_status = fields.Selection([
        ('available', 'Available'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('overload', 'Overload'),
    ], string='Status', compute='_compute_workload_score', store=True)
    workload_status_label = fields.Char(string='Status Label', compute='_compute_workload_status_label')
    last_updated = fields.Datetime(string='Last Updated', default=fields.Datetime.now)

    @api.depends('employee_id', 'project_id')
    def _compute_task_metrics(self):
        today = date.today()
        sprint_start = today - timedelta(days=14)
        for rec in self:
            if not rec.employee_id or not rec.user_id:
                rec.active_tasks_count = 0
                rec.overdue_tasks_count = 0
                rec.completed_tasks_count = 0
                continue
            domain_base = [('user_ids', 'in', rec.user_id.ids)]
            if rec.project_id:
                domain_base.append(('project_id', '=', rec.project_id.id))
            active = self.env['project.task'].search(domain_base + [('is_closed', '=', False)])
            rec.active_tasks_count = len(active)
            overdue = self.env['project.task'].search(domain_base + [
                ('date_deadline', '<', fields.Date.today()),
                ('is_closed', '=', False),
            ])
            rec.overdue_tasks_count = len(overdue)
            completed = self.env['project.task'].search(domain_base + [
                ('is_closed', '=', True),
                ('write_date', '>=', fields.Datetime.to_datetime(str(sprint_start))),
            ])
            rec.completed_tasks_count = len(completed)

    @api.depends('employee_id', 'project_id')
    def _compute_timesheet_metrics(self):
        today = date.today()
        sprint_start = today - timedelta(days=14)
        standard_hours = 80.0
        for rec in self:
            if not rec.employee_id:
                rec.total_timesheet_hours = 0.0
                rec.overtime_hours = 0.0
                continue
            domain = [('employee_id', '=', rec.employee_id.id), ('date', '>=', str(sprint_start))]
            if rec.project_id:
                domain.append(('project_id', '=', rec.project_id.id))
            timesheets = self.env['account.analytic.line'].search(domain)
            total = sum(timesheets.mapped('unit_amount'))
            rec.total_timesheet_hours = total
            rec.overtime_hours = max(0.0, total - standard_hours) # standard_hours = 80.0


    @api.depends('active_tasks_count', 'overdue_tasks_count', 'overtime_hours')
    def _compute_workload_score(self):
        for rec in self:
            score = rec.active_tasks_count * 3.0 + rec.overdue_tasks_count * 5.0 + rec.overtime_hours * 2.0
            rec.workload_score = score
            if score <= 10:
                rec.workload_status = 'available'
            elif score <= 25:
                rec.workload_status = 'normal'
            elif score <= 40:
                rec.workload_status = 'high'
            else:
                rec.workload_status = 'overload'

    @api.depends('workload_status')
    def _compute_workload_status_label(self):
        labels = dict(self._fields['workload_status'].selection)
        for rec in self:
            rec.workload_status_label = labels.get(rec.workload_status, '')

    def action_refresh_metrics(self):
        self._compute_task_metrics()
        self._compute_timesheet_metrics()
        self._compute_workload_score()
        self.last_updated = fields.Datetime.now()

    @api.model
    def cron_refresh_all_metrics(self):
        metrics = self.search([])
        metrics._compute_task_metrics()
        metrics._compute_timesheet_metrics()
        metrics._compute_workload_score()
        metrics.write({'last_updated': fields.Datetime.now()})
