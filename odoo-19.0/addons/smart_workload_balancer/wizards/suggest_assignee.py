from odoo import models, fields, api


class SuggestAssigneeWizard(models.TransientModel):
    _name = 'project.suggest.assignee.wizard'
    _description = 'Suggest Assignee Wizard'

    task_id = fields.Many2one('project.task', string='Task', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Recommended Employees')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        task_id = self.env.context.get('active_id')
        if task_id:
            res['task_id'] = task_id
        return res

    def action_apply(self):
        self.ensure_one()
        task = self.task_id
        if not self.employee_ids:
            return {'type': 'ir.actions.act_window_close'}
        task.write({'recommended_assignee_ids': [(6, 0, self.employee_ids.ids)]})
        task.message_post(body='Recommended assignees updated from the Smart Workload wizard.')
        return {'type': 'ir.actions.act_window_close'}
