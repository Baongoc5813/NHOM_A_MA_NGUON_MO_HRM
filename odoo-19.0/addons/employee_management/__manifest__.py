{
    'name': 'Employee Management',
    'version': '1.0',
    'author': 'Your Name',
    'category': 'Custom',
    'summary': 'Module quản lý nhân viên',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_view.xml',
        'views/employee_menu.xml',
    ],
    'installable': True,
    'application': True,
}