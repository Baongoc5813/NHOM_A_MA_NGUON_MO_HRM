{
'name': 'Hospital Patient',
'version': '1.0',
'author': 'Mintsduc',
'category': 'Custom',
'summary': 'Module quản lý bệnh nhân và bác sĩ phụ trách',
'depends': ['base'],
'data': [
'security/ir.model.access.csv',
'views/patient_view.xml',
'views/doctor_view.xml',
'views/patient_menu.xml',
],
'installable': True,
'application': True,
}