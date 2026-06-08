{
    'name': 'Hello Odoo',
    'version': '1.0',
    'summary': 'Module hiển thị thông điệp Hello Odoo',
    'category': 'Custom',
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv', # Dòng này giúp hiện App
        'views/hello_view.xml',
        'views/hello_menu.xml',         # Dòng này giúp hiện Menu
    ],
    'installable': True,
    'application': True, # Dòng này giúp App hiện ra trong danh sách Apps chính
}