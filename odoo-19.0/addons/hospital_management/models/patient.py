from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Thông tin bệnh nhân'

    name = fields.Char(string="Tên bệnh nhân", required=True)
    birth_year = fields.Integer(string='Năm sinh')
    age = fields.Integer(string='Tuổi', compute='_compute_age', store=True)
    disease = fields.Text(string="Mô tả bệnh")
    doctor_id = fields.Many2one('res.partner', string="Bác sĩ phụ trách")

    need_parent = fields.Boolean(string="Cần phụ huynh", compute="_compute_need_parent", store=True)
    @api.depends('birth_year')
    def _compute_age(self):
        current_year = date.today().year
        for rec in self:
            if rec.birth_year > 0:
                rec.age = current_year - rec.birth_year
            else:
                rec.age = 0

    @api.depends('age')
    def _compute_need_parent(self):
        for rec in self:
            if rec.age < 10 and rec.age > 0:
                rec.need_parent = True
            else:
                rec.need_parent = False

    @api.constrains('age')
    def _check_age_valid(self):
        for rec in self:
            if rec.age < 0:
                raise ValidationError(_("Tuổi bệnh nhân không được nhỏ hơn 0"))

    def update_patient_disease(self, new_disease):
        for rec in self:
            rec.write({'disease': new_disease})