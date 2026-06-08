from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    onboarding_status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Onboarding Status', default='not_started', tracking=True)

    assigned_device = fields.Char(
        string='Assigned Device'
    )

    onboarding_request_id = fields.Many2one(
        'hr.onboarding.request',
        string='Onboarding Request'
    )

    def action_start_onboarding(self):
        """ Manually trigger onboarding process from the Employee profile, 
            generating a main request and 3 aligned standard tasks. """
        self.ensure_one()
        current_user_id = self.env.user.id

        # 1. Create the main Onboarding Request
        request = self.env['hr.onboarding.request'].create({
            'name': f'Onboarding - {self.name}',
            'employee_id': self.id,
            'state': 'in_progress',
            'user_id': current_user_id
        })

        # Update status and relation on Employee form
        self.write({
            'onboarding_status': 'in_progress',
            'onboarding_request_id': request.id
        })

        # 2. Extract device details and define task names
        device_info = self.assigned_device if self.assigned_device else "Undefined"
        
        # 3. Bulk create the exactly 3 corresponding tasks
        self.env['hr.onboarding.task'].create([
            {
                'name': f'Prepare Laptop ({device_info})',
                'request_id': request.id,
                'assigned_department': 'it',
                'user_id': current_user_id
            },
            {
                'name': 'Prepare Employee Documents',
                'request_id': request.id,
                'assigned_department': 'hr',
                'user_id': current_user_id
            },
            {
                'name': 'Assign Project',
                'request_id': request.id,
                'assigned_department': 'project',
                'user_id': current_user_id
            }
        ])

        # Redirect the screen directly to the newly created Onboarding Form
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.onboarding.request',
            'view_mode': 'form',
            'res_id': request.id,
            'target': 'current',
        }