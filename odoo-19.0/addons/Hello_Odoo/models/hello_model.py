from odoo import models, fields

class HelloModel(models.Model):
    _name = 'hello.message'
    _description = 'Hello Message Model'

    name = fields.Char(string='Message', default='HELLO ODOO', required=True)