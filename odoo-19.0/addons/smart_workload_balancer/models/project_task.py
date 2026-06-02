from odoo import models, fields, api, _
from odoo.fields import Command
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    recommended_assignee_ids = fields.Many2many(
        'hr.employee', 'task_recommended_employee_rel', 'task_id', 'employee_id',
        string='Recommended Employees', readonly=True
    )
    override_reason = fields.Text(string='Reason for Override')
    show_override_reason = fields.Boolean(compute='_compute_show_override', store=False)
    workload_warning = fields.Html(compute='_compute_workload_warning', store=False)

    def _get_project_candidate_users(self):
        self.ensure_one()
        project = self.project_id
        users = project.favorite_user_ids | project.user_id
        if not users:
            users = project.message_partner_ids.user_ids
        return users.filtered(lambda user: user.active and not user.share)

    @api.depends('user_ids', 'recommended_assignee_ids')
    def _compute_show_override(self):
        for task in self:
            if not task.recommended_assignee_ids or not task.user_ids:
                task.show_override_reason = False
                continue
            rec_user_ids = task.recommended_assignee_ids.mapped('user_id.id')
            task.show_override_reason = bool(
                task.user_ids.ids and not all(uid in rec_user_ids for uid in task.user_ids.ids)
            )

    @api.depends('user_ids')
    def _compute_workload_warning(self):
        for task in self:
            warnings = []
            for user in task.user_ids:
                employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
                if not employee:
                    continue
                metric = self.env['project.workload.metric'].search([('employee_id', '=', employee.id)], limit=1)
                if metric and metric.workload_status == 'overload':
                    warnings.append(
                        f'<span style="color:red">&#9888; <b>{employee.name}</b> is OVERLOADED '
                        f'({metric.active_tasks_count} tasks, {metric.overdue_tasks_count} overdue)</span>'
                    )
                elif metric and metric.workload_status == 'high':
                    warnings.append(
                        f'<span style="color:orange">&#9889; <b>{employee.name}</b> has HIGH workload '
                        f'({metric.active_tasks_count} tasks)</span>'
                    )
            task.workload_warning = '<br/>'.join(warnings) if warnings else False

    def action_suggest_assignee(self):
        self.ensure_one()
        if not self.project_id:
            raise UserError(_('Please select a Project before suggesting assignees.'))
        project_members = self._get_project_candidate_users()
        if not project_members:
            raise UserError(_('The project has no internal members. Please add members/followers or a Project Manager to the project.'))
        rule = self.env['project.assignment.rule'].search(
            [('project_id', '=', self.project_id.id), ('active', '=', True)], limit=1
        )
        max_tasks = rule.max_task_threshold if rule else 8
        max_overtime = rule.max_overtime_threshold if rule else 10.0
        candidates = []
        for user in project_members:
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            if not employee:
                continue
            metric = self.env['project.workload.metric'].search([('employee_id', '=', employee.id)], limit=1)
            if metric:
                if metric.active_tasks_count >= max_tasks or metric.overtime_hours >= max_overtime:
                    continue
                score, active, overdue = metric.workload_score, metric.active_tasks_count, metric.overdue_tasks_count
            else:
                metric = self.env['project.workload.metric'].create({
                    'employee_id': employee.id,
                    'project_id': self.project_id.id,
                })
                score, active, overdue = 0, 0, 0
            candidates.append({'employee': employee, 'score': score, 'active': active, 'overdue': overdue})
        if not candidates:
            raise UserError(_('All members are currently overloaded.'))
        candidates.sort(key=lambda x: x['score'])
        top = candidates[:3]
        self.recommended_assignee_ids = [Command.set([c['employee'].id for c in top])]
        lines = ['<b>System Recommended Assignees:</b><br/>']
        for i, c in enumerate(top, 1):
            lines.append(f'{i}. <b>{c["employee"].name}</b> - Score: {c["score"]:.1f} | Tasks: {c["active"]} | Overdue: {c["overdue"]}<br/>')
        self.message_post(body=''.join(lines))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Suggest Assignees',
                'message': f'The system recommended {len(top)} suitable employees.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_confirm_override(self):
        self.ensure_one()
        if not self.override_reason:
            raise UserError(_('Please enter a reason when choosing someone outside the recommended list.'))
        self.message_post(body=f'<b>PM recorded an override</b><br/>Reason: {self.override_reason}')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': 'Reason Saved', 'message': 'The reason has been saved to the log.', 'type': 'info'}
        }

    def _check_and_notify_overload(self):
        for task in self:
            if not task.project_id:
                continue
            rule = self.env['project.assignment.rule'].search([('project_id', '=', task.project_id.id)], limit=1)
            max_tasks = rule.max_task_threshold if rule else 8
            for user in task.user_ids:
                employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
                if not employee:
                    continue
                metric = self.env['project.workload.metric'].search([('employee_id', '=', employee.id)], limit=1)
                if metric and metric.workload_status == 'overload':
                    pm = task.project_id.user_id
                    if pm:
                        self.env['mail.message'].create({
                            'model': 'project.project',
                            'res_id': task.project_id.id,
                            'message_type': 'notification',
                            'subtype_id': self.env.ref('mail.mt_note').id,
                            'body': (
                                f'<b>OVERLOAD WARNING</b><br/>'
                                f'Employee <b>{employee.name}</b> is currently overloaded:<br/>'
                                f'Tasks: {metric.active_tasks_count}/{max_tasks} | '
                                f'Overdue: {metric.overdue_tasks_count} | '
                                f'Overtime: {metric.overtime_hours:.1f}h'
                            ),
                            'partner_ids': [(4, pm.partner_id.id)],
                        })

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        tasks._check_and_notify_overload()
        return tasks

    def write(self, vals):
        res = super().write(vals)
        if 'user_ids' in vals:
            self._check_and_notify_overload()
        return res
