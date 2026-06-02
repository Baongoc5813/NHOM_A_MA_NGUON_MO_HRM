import hashlib
from odoo import http, fields
from odoo.http import request


class CandidatePortal(http.Controller):

    @http.route('/candidate-portal/status', type='http', auth='public', website=True)
    def status(self, token=None, **kwargs):
        if not token:
            return request.render('candidate_portal.portal_error', {'msg': 'Thiếu token'})
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        applicant = request.env['hr.applicant'].sudo().search([
            ('portal_token', '=', token_hash)
        ], limit=1)
        if not applicant or applicant.portal_token_expiry < fields.Datetime.now():
            return request.render('candidate_portal.portal_error', {'msg': 'Link hết hạn hoặc không hợp lệ'})
        # Build ordered list of stages for this job (job-specific + global)
        stage_model = request.env['hr.recruitment.stage'].sudo()
        stages = stage_model.search([
            ('job_ids', 'in', [applicant.job_id.id, False]),
            ('fold', '=', False),
        ], order='sequence')
        # map stage id to its index for template logic
        positions = {sid: idx for idx, sid in enumerate(stages.ids)}
        try:
            current_index = positions.get(applicant.stage_id.id, -1)
        except Exception:
            current_index = -1

        return request.render('candidate_portal.portal_status', {
            'applicant': applicant,
            'stages': stages,
            'current_index': current_index,
            'positions': positions,
        })
