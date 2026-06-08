from odoo import models, fields

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string="Tên sách", required=True)
    author = fields.Char(string="Tác giả")
    isbn = fields.Char(string="Mã ISBN")
    quantity = fields.Integer(string="Số lượng còn", default=1)
    description = fields.Text(string="Mô tả")
    image = fields.Binary(string="Ảnh bìa")
    state = fields.Selection([
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock')
    ], string="Trạng thái", default='available')