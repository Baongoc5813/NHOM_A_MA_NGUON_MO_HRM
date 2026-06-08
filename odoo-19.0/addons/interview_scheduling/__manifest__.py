# -*- coding: utf-8 -*-
{
    'name': 'Interview Scheduling & Tracking',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Recruitment',
    'summary': 'Automated interview scheduling, feedback and attendance tracking',
    'author': 'NovaSync',
    'depends': [
        'hr_recruitment',
        'calendar',
        'mail',
    ],
    'data': [
        'security/interview_security.xml',
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'views/hr_interview_feedback_views.xml',
        'views/calendar_event_views.xml',
        'views/hr_applicant_views.xml',
        'views/wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
