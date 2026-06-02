# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields, api

class HrTalentPool(models.Model):
    _inherit = 'hr.talent.pool'

    match_score = fields.Float(string='Match Score (%)', default=0.0, digits=(5, 2))
    potential_score = fields.Float(string='Past Interview Score', default=0.0)
    reengagement_status = fields.Selection([
        ('none', 'Not Contacted'),
        ('contacted', 'Contacted (Email Sent)'),
        ('updated', 'CV Updated via Portal'),
        ('failed', 'No Response')
    ], string='Re-engagement Status', default='none', tracking=True)
    
    access_token = fields.Char(string='Access Token', default=lambda self: str(uuid.uuid4()), copy=False)

    def action_generate_token(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        for record in self:
            if not record.access_token:
                record.access_token = str(uuid.uuid4())

    def action_send_reconnect_email(self):
        """Server Action: post reconnect notice to candidate chatter using rendered template (with button)."""
        template = self.env.ref('hr_recruitment_talent_matching.email_template_reconnect_candidate', raise_if_not_found=False)
        if not template:
            return False
        for record in self:
            for applicant in record.talent_ids:
                # ensure applicant has a token
                if hasattr(applicant, 'action_generate_token'):
                    applicant.action_generate_token()
                # Render the template body_html for this applicant
                try:
                    ctx = dict(self.env.context)
                    ctx.update({
                        'active_model': 'hr.applicant',
                        'active_id': applicant.id,
                        'default_model': 'hr.applicant',
                        'default_res_id': applicant.id,
                        'lang': applicant.partner_id.lang or applicant.env.user.lang,
                    })
                    body = template.with_context(ctx).render_template(template.body_html, 'hr.applicant', applicant.id)
                    subject = template.with_context(ctx).render_template(template.subject, 'hr.applicant', applicant.id)
                    applicant.message_post(body=body, subject=subject, subtype_xmlid='mail.mt_comment')
                except Exception as e:
                    continue
                try:
                    applicant.write({'reengagement_status': 'contacted'})
                except Exception:
                    pass
        return True