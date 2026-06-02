# -*- coding: utf-8 -*-
{
    'name': 'Talent Pool Auto-Matching & Re-engagement',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Recruitment',
    'summary': 'Automate candidate matching and re-engagement from talent pool.',
    'description': """
        This module extends the Odoo Recruitment process by adding automated skill matching,
        candidate shortlist generation based on weights, and automated email re-engagement workflows via Portal.
    """,
    'author': 'Trần Nguyễn Minh Đức',
    'depends': ['hr_recruitment', 'hr_skills', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'data/automation_action_data.xml',
        'views/hr_matching_rule_views.xml',
        'views/hr_talent_pool_views.xml',
        'views/hr_job_views.xml',
        'views/portal_templates.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}