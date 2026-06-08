# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    interview_score = fields.Float(string='Interview Score (1-100)', default=0.0)
    potential_score = fields.Float(string='Past Interview Score', default=0.0)
    match_score = fields.Float(string='Match Score (%)', default=0.0, digits=(5, 2))
    
    reengagement_status = fields.Selection([
        ('none', 'Not Contacted'),
        ('contacted', 'Contacted (Email Sent)'),
        ('updated', 'CV Updated via Portal'),
        ('failed', 'No Response')
    ], string='Re-engagement Status', default='none', tracking=True)
    
    access_token = fields.Char(string='Access Token', default=lambda self: str(uuid.uuid4()), copy=False)

    def action_generate_token(self):
        for record in self:
            if not record.access_token:
                record.access_token = str(uuid.uuid4())

    def action_send_reconnect_email(self):
        for record in self:
            # 1. Chặn lỗi ngầm nếu thiếu email
            if not record.email_from:
                record.message_post(
                    body="⚠️ HỆ THỐNG TỪ CHỐI: Không thể gửi email vì hồ sơ ứng viên này đang bị trống địa chỉ Email.",
                    subtype_xmlid='mail.mt_note'
                )
                continue

            # 2. Sinh Token
            record.action_generate_token()
            
            # 3. ÉP BÁO LỖI: Đổi thành raise_if_not_found=True để không bị "im ru" nếu thiếu XML
            template = self.env.ref('hr_recruitment_talent_matching.email_template_reconnect_applicant_v3', raise_if_not_found=True)
            
            # 4. Render nội dung
            rendered_body = template._render_field('body_html', record.ids)[record.id]
            rendered_subject = template._render_field('subject', record.ids)[record.id]
            
            # 5. Gửi thư (đã bỏ force_send=True để tránh kẹt mạng ở máy localhost)
            template.send_mail(record.id, force_send=True)

            # 6. Vẽ phong bì thư đỏ lên Chatter
            record.message_post(
                body=rendered_body,
                subject=rendered_subject,
                message_type='email',
                subtype_xmlid='mail.mt_comment'
            )
                
            # 7. Cập nhật trạng thái
            record.write({'reengagement_status': 'contacted'})
            
        # TỰ ĐỘNG TẢI LẠI TRANG: Ép trình duyệt F5 để hiển thị Chatter ngay lập tức!
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def write(self, vals):
        if 'interview_score' in vals:
            vals['potential_score'] = vals['interview_score']
        return super(HrApplicant, self).write(vals)