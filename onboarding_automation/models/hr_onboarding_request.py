from odoo import models, fields, api


class HrOnboardingRequest(models.Model):
    _name = 'hr.onboarding.request'
    _description = 'Onboarding Request'
    _order = 'id desc'

    name = fields.Char(
        string='Onboarding Request',
        required=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade'
    )
   
    onboarding_date = fields.Date(
        string='Onboarding Date',
        default=fields.Date.context_today
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status', default='draft', tracking=True)

    user_id = fields.Many2one(
        'res.users', 
        string='Coordinator', 
        default=lambda self: self.env.user,
        tracking=True
    )

    task_ids = fields.One2many(
        'hr.onboarding.task',
        'request_id',
        string='Tasks'
    )

    # Giữ lại ô Contact Email lấy từ Employee qua để chữa cháy, rất tiện và an toàn
    employee_email = fields.Char(
        string='Contact Email', 
        related='employee_id.work_email', 
        readonly=True
    )

    def action_start_onboarding(self):
        """ Activate onboarding process and create standard template tasks """
        for record in self:
            if record.state == 'draft':
                record.state = 'in_progress'
                
                if record.employee_id:
                    record.employee_id.onboarding_status = 'in_progress'

                device_info = record.employee_id.assigned_device if record.employee_id.assigned_device else "Undefined"
                current_user_id = self.env.user.id
                
                # Tạo các task cơ bản bằng tiếng Anh đồng bộ
                self.env['hr.onboarding.task'].create([
                    {
                        'name': f'Prepare Laptop ({device_info})',
                        'request_id': record.id,
                        'assigned_department': 'it',
                        'user_id': current_user_id
                    },
                    {
                        'name': 'Create Corporate Email Account',
                        'request_id': record.id,
                        'assigned_department': 'it',
                        'user_id': current_user_id
                    },
                    {
                        'name': 'Prepare Employee Documents',
                        'request_id': record.id,
                        'assigned_department': 'hr',
                        'user_id': current_user_id
                    },
                    {
                        'name': 'Assign Project',
                        'request_id': record.id,
                        'assigned_department': 'project',
                        'user_id': current_user_id
                    }
                ])

    @api.model_create_multi
    def create(self, vals_list):
        requests = super(HrOnboardingRequest, self).create(vals_list)
        for req in requests:
            if req.state == 'in_progress' and req.employee_id:
                req.employee_id.onboarding_status = 'in_progress'
                req.employee_id.onboarding_request_id = req.id
        return requests