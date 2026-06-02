import secrets
import hashlib
from datetime import timedelta
import secrets, hashlib
from datetime import timedelta
from odoo import models, fields


class HrApplicantPortal(models.Model):
    _inherit = 'hr.applicant'

    portal_token = fields.Char(string='Portal Token Hash')
    portal_token_expiry = fields.Datetime(string='Token Expiry')

    def action_send_portal_link(self):
        self.ensure_one()
        raw_token = secrets.token_urlsafe(32)
        self.portal_token = hashlib.sha256(raw_token.encode()).hexdigest()
        self.portal_token_expiry = fields.Datetime.now() + timedelta(days=7)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        portal_url = f"{base_url}/candidate-portal/status?token={raw_token}"
        self.env['mail.mail'].create({
            'subject': f'Cập nhật hồ sơ ứng tuyển - {self.job_id.name or ""}',
            'email_to': self.email_from,
            'body_html': f"""
                <p>Xin chào <strong>{self.partner_name}</strong>,</p>
                <p>Hồ sơ của bạn cho vị trí <strong>{self.job_id.name or ''}</strong> đang được xem xét.</p>
                <p>Bấm link bên dưới để xem trạng thái hồ sơ:</p>
                <p><a href="{portal_url}">{portal_url}</a></p>
                <p>Link có hiệu lực 7 ngày.</p>
            """,
        }).send()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'message': 'Đã gửi link portal đến ứng viên', 'type': 'success'},
        }
