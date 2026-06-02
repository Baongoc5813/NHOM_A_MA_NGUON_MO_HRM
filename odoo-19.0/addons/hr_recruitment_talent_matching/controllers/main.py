# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request

class TalentPoolPortal(http.Controller):

    @http.route('/talent/reconnect/<string:token>', type='http', auth='public', website=True)
    def talent_reconnect_form(self, token, **kwargs):
        # Lấy ứng viên theo access_token, bao gồm cả các ứng viên đã bị từ chối (Refused)
        candidate = request.env['hr.applicant'].sudo().with_context(active_test=False).search([('access_token', '=', token)], limit=1)
        
        if not candidate:
            return request.render('website.page_404')
        
        return request.render('hr_recruitment_talent_matching.portal_candidate_update_cv_template', {
            'candidate': candidate,
            'token': token
        })

    @http.route('/talent/reconnect/<string:token>/submit', type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def talent_reconnect_submit(self, token, **kwargs):
        # Tìm ứng viên theo access_token, bao gồm cả các ứng viên đã bị từ chối (Refused)
        candidate = request.env['hr.applicant'].sudo().with_context(active_test=False).search([('access_token', '=', token)], limit=1)
        
        if not candidate:
            return request.render('website.page_404')

        vals = {}
        if kwargs.get('phone'):
            vals['partner_phone'] = kwargs.get('phone')
        if kwargs.get('email'):
            vals['email_from'] = kwargs.get('email')
            
        if kwargs.get('ufile'):
            uploaded_file = kwargs.get('ufile')
            filename = uploaded_file.filename
            file_content = uploaded_file.read()
            
            if file_content:
                request.env['ir.attachment'].sudo().create({
                    'name': filename,
                    'res_model': 'hr.applicant', # Đính kèm file vào bảng hr.applicant
                    'res_id': candidate.id,
                    'type': 'binary',
                    'datas': base64.b64encode(file_content),
                })
            
        candidate.write(vals)
        # Cập nhật trạng thái sang 'updated' khi ứng viên cập nhật CV qua portal
        candidate.write({'reengagement_status': 'updated'})
        # Ghi log vào lịch sử (Chatter) để HR biết ứng viên đã cập nhật hồ sơ
        candidate.message_post(
            body="<b>System:</b> The candidate has proactively updated their profile information and uploaded a new CV via the Portal Reconnect page.",
            subtype_xmlid="mail.mt_comment"
        )
        
        return request.render('hr_recruitment_talent_matching.portal_candidate_success_template')