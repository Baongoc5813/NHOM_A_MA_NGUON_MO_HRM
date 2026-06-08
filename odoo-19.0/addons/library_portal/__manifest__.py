{
    'name': 'Library Portal',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Quản lý sách và cho phép khách đăng ký mượn sách qua website',
    'author': 'Trần Nguyễn Minh Đức',
    'depends': ['base', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/library_book_views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}