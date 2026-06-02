{
    'name': 'Smart Workload Balancer',
    'version': '19.0.1.0.0',
    'category': 'Project',
    'summary': 'Smart Workload Balancer for project task assignment and workload monitoring',
    'depends': ['project', 'hr_timesheet', 'hr', 'mail', 'product'],
    'data': [
        'security/workload_security.xml',
        'security/ir.model.access.csv',
        'data/workload_cron.xml',
        'data/demo_workload_data.xml',
        'views/workload_metric_views.xml',
        'views/assignment_rule_views.xml',
        'views/project_task_views.xml',
        'views/workload_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'smart_workload_balancer/static/src/css/workload.css',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}