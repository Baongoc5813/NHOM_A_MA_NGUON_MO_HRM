from odoo import models, fields, api
from datetime import date

class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Bác sĩ'

    name = fields.Char(string='Tên bác sĩ', required=True)
    phone = fields.Char(string='Số điện thoại')
    email = fields.Char(string='Email')
    birth_year = fields.Integer(string='Năm sinh')
    # Age là trường tính toán (compute) dựa trên năm sinh
    age = fields.Integer(string='Tuổi', compute='_compute_age', store=True)
    department = fields.Char(string='Chuyên khoa')
    manager_id = fields.Many2one('res.partner', string='Quản lý')

    state = fields.Selection([
        ('available', 'Sẵn sàng'),
        ('busy', 'Đang khám'),
        ('away', 'Vắng mặt'),
        ('retired', 'Nghỉ hưu')
    ], string='Trạng thái', default='available')

    @api.depends('birth_year')
    def _compute_age(self):
        current_year = date.today().year
        for rec in self:
            if rec.birth_year > 1900: 
                rec.age = current_year - rec.birth_year
            else:
                rec.age = 0