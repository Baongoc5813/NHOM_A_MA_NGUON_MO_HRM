from odoo import models


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def action_create_employee(self):

        res = super().action_create_employee()

        for applicant in self:

            onboarding = self.env[
                'hr.onboarding.request'
            ].create({
                'name': applicant.partner_name,
                'employee_id': applicant.emp_id.id,
                'state': 'in_progress'
            })

            task_list = [
                {
                    'name': 'Prepare Laptop',
                    'assigned_department': 'it'
                },
                {
                    'name': 'Create Company Email',
                    'assigned_department': 'it'
                },
                {
                    'name': 'Prepare Labor Contract',
                    'assigned_department': 'hr'
                },
                {
                    'name': 'Assign Project',
                    'assigned_department': 'project'
                }
            ]

            for task in task_list:

                self.env[
                    'hr.onboarding.task'
                ].create({
                    'name': task['name'],
                    'assigned_department':
                        task['assigned_department'],
                    'request_id': onboarding.id
                })

        return res