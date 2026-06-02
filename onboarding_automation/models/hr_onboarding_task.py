from odoo import models, fields


class HrOnboardingTask(models.Model):
    _name = 'hr.onboarding.task'
    _description = 'Onboarding Task'

    name = fields.Char(string='Task')

    request_id = fields.Many2one(
        'hr.onboarding.request',
        string='Onboarding Request'
    )

    assigned_department = fields.Selection([
        ('hr', 'HR'),
        ('it', 'IT'),
        ('project', 'Project')
    ], string='Department')

    deadline = fields.Date(string='Deadline')
    user_id = fields.Many2one('res.users', string='Assigned To')

    state = fields.Selection([
        ('todo', 'To Do'),
        ('done', 'Done')
    ], default='todo')

    def write(self, vals):

        res = super().write(vals)

        for task in self:

            request = task.request_id

            all_done = all(
                t.state == 'done'
                for t in request.task_ids
            )

            if all_done:

                request.state = 'done'

                request.employee_id.write({
                    'onboarding_status': 'done'
                })

        return res