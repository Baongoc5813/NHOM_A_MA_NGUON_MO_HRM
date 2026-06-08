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
        """Server Action: send reconnect email to candidates from talent pool."""
        template = self.env.ref('hr_recruitment_talent_matching.email_template_reconnect_candidate', raise_if_not_found=False)
        if not template:
            return False
        
        for record in self:
            for applicant in record.talent_ids:
                # Ensure applicant has a valid email
                if not applicant.email_from:
                    continue
                
                # Generate token if needed
                if hasattr(applicant, 'action_generate_token'):
                    applicant.action_generate_token()
                
                try:
                    # Send actual email using template
                    template.send_mail(applicant.id, force_send=True)
                    
                    # Update status
                    applicant.write({'reengagement_status': 'contacted'})
                    
                    # Log to chatter
                    applicant.message_post(
                        body="✉️ Re-engagement email sent from talent pool",
                        subtype_xmlid='mail.mt_note'
                    )
                except Exception as e:
                    applicant.message_post(
                        body=f"❌ Failed to send email: {str(e)}",
                        subtype_xmlid='mail.mt_note'
                    )
        
        return True