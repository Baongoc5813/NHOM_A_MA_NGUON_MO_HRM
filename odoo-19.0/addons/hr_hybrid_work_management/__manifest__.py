{
    'name': 'Hybrid Work & WFH Management',
    'version': '19.0.1.0.0',
    'summary': 'Manage Hybrid Work and Work From Home requests',
    'description': '''
Hybrid Work & Work From Home Management module.
Employees can create WFH/Hybrid requests and managers can approve or reject them.
    ''',
    'category': 'Human Resources',
    'author': 'Nhom A',
    'depends': ['base', 'hr', 'hr_attendance', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/hybrid_request_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}