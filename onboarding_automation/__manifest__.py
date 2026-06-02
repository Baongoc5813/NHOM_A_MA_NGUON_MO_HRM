{
    'name': 'Onboarding Automation',
    'version': '1.0',
    'summary': 'Automated Employee Onboarding',
    'category': 'Human Resources',
    'author': 'Phương Quỳnh',

    'depends': [
        'hr_recruitment',
        'hr',
        'stock',
        'hr_attendance',
        'project'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/onboarding_views.xml',
        'views/hr_employee_views.xml',
        #'views/it_asset_request_views.xml',
    ],

    'installable': True,
    'application': True,
}