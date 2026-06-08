from odoo import http
from odoo.http import request

class LibraryController(http.Controller):

    # 1. Trang danh sách sách: Chỉ hiện sách available và số lượng > 0
    @http.route('/library/books', type='http', auth='public', website=True)
    def list_books(self, **kwargs):
        # Lọc theo yêu cầu mới của bạn 
        domain = [('state', '=', 'available'), ('quantity', '>', 0)]
        books = request.env['library.book'].sudo().search(domain)
        return request.render('library_portal.books_list_template', {'books': books})

    # 2. Trang chi tiết sách [cite: 43]
    @http.route('/library/book/<model("library.book"):book>', type='http', auth='public', website=True)
    def book_detail(self, book, **kwargs):
        if not book.exists():
            return request.not_found() # Trả về 404 nếu không tồn tại [cite: 47]
        return request.render('library_portal.book_detail_template', {'book': book})

    # 3. Form đăng ký mượn sách (GET) [cite: 48, 49]
    @http.route('/library/borrow/<model("library.book"):book>', type='http', auth='public', website=True)
    def borrow_form(self, book, **kwargs):
        return request.render('library_portal.borrow_form_template', {
            'book': book, 
            'error': kwargs.get('error'),
            'form_data': kwargs
        })

    # 4. Xử lý dữ liệu form (POST) [cite: 50]
    @http.route('/library/borrow/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def borrow_submit(self, **post):
        name = post.get('name')
        email = post.get('email')
        book_id = post.get('book_id')

        # Validate dữ liệu: email phải có @ và name không để trống [cite: 51]
        if not name or not email or '@' not in email:
            book = request.env['library.book'].sudo().browse(int(book_id))
            return request.render('library_portal.borrow_form_template', {
                'book': book,
                'error': "Dữ liệu lỗi: Email phải chứa @ và Tên không được để trống.",
                'form_data': post # Giữ nguyên giá trị đã nhập [cite: 52]
            })

        # Nếu dữ liệu hợp lệ: tạo bản ghi library.borrow.request 
        borrow_req = request.env['library.borrow.request'].sudo().create({
            'name': name,
            'email': email,
            'phone': post.get('phone'),
            'book_id': int(book_id)
        })

        # Sau đó redirect sang trang cảm ơn kèm tham số id của request 
        return request.redirect(f'/library/borrow/thank-you?request_id={borrow_req.id}')

    # 5. Trang cảm ơn 
    @http.route('/library/borrow/thank-you', type='http', auth='public', website=True)
    def borrow_thank_you(self, **kwargs):
        # Lấy tham số request_id từ URL để hiển thị
        request_id = kwargs.get('request_id')
        return request.render('library_portal.thank_you_template', {'request_id': request_id})