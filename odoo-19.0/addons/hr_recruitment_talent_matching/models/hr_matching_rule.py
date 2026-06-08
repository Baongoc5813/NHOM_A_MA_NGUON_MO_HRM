# -*- coding: utf-8 -*-
from odoo import models, fields

class HrMatchingRule(models.Model):
    _name = 'hr.matching.rule'
    _description = 'Matching Rules based on Tags'

    name = fields.Char(string='Rule Name', required=True)
    rule_type = fields.Selection([
        ('tag_matching', 'Tag Matching'),
        ('interview_score', 'Interview Score')
    ], string='Rule Type', default='tag_matching', required=True)
    
    # Trường liên kết với bảng Tag (Kỹ năng) của Odoo
    tag_ids = fields.Many2many('hr.applicant.category', string='Required Tags')
    
    weight = fields.Float(string='Weight (%)', default=100.0)
    active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)