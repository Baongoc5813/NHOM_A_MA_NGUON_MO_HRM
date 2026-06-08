from odoo import models, fields

class Employee(models.Model):
    _name = 'employee.management'
    _description = 'Employee Management'
    
    name = fields.Char(string='Tên', required=True)
    age = fields.Integer(string='Tuổi')
    department = fields.Char(string='Phòng ban')