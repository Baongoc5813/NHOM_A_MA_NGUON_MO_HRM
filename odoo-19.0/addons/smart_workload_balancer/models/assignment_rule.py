from odoo import models, fields, api


class ProjectAssignmentRule(models.Model):
    _name = 'project.assignment.rule'
    _description = 'Task Assignment Rule'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string='Project', required=True, ondelete='cascade')
    max_task_threshold = fields.Integer(string='Max Tasks per Employee', default=8)
    max_overtime_threshold = fields.Float(string='Max Overtime Hours', default=10.0)
    max_overdue_threshold = fields.Integer(string='Max Overdue Tasks', default=3)
    skill_weight = fields.Float(string='Skill Weight (%)', default=40.0)
    workload_weight = fields.Float(string='Workload Weight (%)', default=60.0)
    active = fields.Boolean(default=True)
    note = fields.Text(string='Note')

    @api.constrains('skill_weight', 'workload_weight')
    def _check_weights(self):
        for rec in self:
            total = rec.skill_weight + rec.workload_weight
            if abs(total - 100.0) > 0.01:
                from odoo.exceptions import ValidationError
                raise ValidationError(f'The total weight must equal 100%. Current total: {total}%')