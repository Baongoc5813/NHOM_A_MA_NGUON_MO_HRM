from odoo import models, fields

class LibraryBorrowRequest(models.Model):
    _name = 'library.borrow.request'
    _description = 'Borrow Request'

    name = fields.Char(string="Tên người mượn")
    email = fields.Char(string="Email", required=True)
    phone = fields.Char(string="Số điện thoại")
    book_id = fields.Many2one('library.book', string="Sách", required=True)
    request_date = fields.Datetime(string="Ngày yêu cầu", default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected')
    ], string="Trạng thái", default='draft')