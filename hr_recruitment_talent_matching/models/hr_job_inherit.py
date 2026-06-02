# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HrJob(models.Model):
    _inherit = 'hr.job'

    # Trường liên kết để HR chọn Quy tắc so khớp áp dụng riêng cho Vị trí công việc này
    matching_rule_id = fields.Many2one(
        'hr.matching.rule', 
        string='Applied Matching Rule', 
        domain=[('active', '=', True)]
    )
    
    # Trường tính toán số lượng ứng viên lọt vào danh sách Shortlist (Điểm Match >= 50%)
    shortlist_count = fields.Integer(
        string='Shortlist Count', 
        compute='_compute_shortlist_count'
    )

    def _compute_shortlist_count(self):
        for job in self:
            # Đếm số lượng ứng viên bị từ chối/lưu trữ (kho Talent Pool) có điểm match >= 50%
            candidates = self.env['hr.applicant'].search([
                ('active', '=', False), 
                ('match_score', '>=', 50.0)
            ])
            job.shortlist_count = len(candidates)

    def action_view_shortlist(self):
        self.ensure_one()
        # Tự động tính toán/cập nhật lại toàn bộ điểm số của kho ứng viên trước khi mở giao diện
        self._calculate_matching_scores()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Danh sách Gợi ý Shortlist - {self.name}',
            'res_model': 'hr.applicant',
            'view_mode': 'list,form',
            # Chỉ hiển thị những ứng viên có độ tương thích từ 50% trở lên
            'domain': [('active', '=', False), ('match_score', '>=', 50.0)],
            'context': {
                'default_job_id': self.id,
                'search_default_job_id': self.id
            },
            'order': 'match_score desc', # Ứng viên điểm cao nhất xếp lên đầu
        }

    def _calculate_matching_scores(self):
        """
        THUẬT TOÁN ĐỐI KHỚP THEO TAG KỸ NĂNG VÀ ĐIỂM SỐ
        """
        # Tìm quy tắc so khớp được áp dụng riêng cho Vị trí công việc này
        rule = self.matching_rule_id
        # Lấy toàn bộ kho ứng viên cũ đã lưu trữ (Talent Pool dữ liệu nguồn)
        candidates = self.env['hr.applicant'].search([('active', '=', False)])
        
        if not candidates:
            return
            
        # Nếu Job chưa được gán Quy tắc so khớp nào, reset điểm match của kho ứng viên về 0%
        if not rule or not rule.active:
            candidates.write({'match_score': 0.0})
            return

        for candidate in candidates:
            final_score = 0.0
            
            # XỬ LÝ LOẠI 1: ĐỐI KHỚP THEO DANH SÁCH TAG KỸ NĂNG (Tag Matching)
            if rule.rule_type == 'tag_matching' and rule.tag_ids:
                required_tag_ids = set(rule.tag_ids.ids)
                candidate_tag_ids = set(candidate.categ_ids.ids)
                
                # Tìm các Tag trùng nhau giữa Ứng viên và Quy tắc
                matching_tags = required_tag_ids.intersection(candidate_tag_ids)
                
                # Tính toán tỷ lệ phần trăm dựa trên số lượng tag trùng khớp
                if required_tag_ids:
                    final_score = (len(matching_tags) / len(required_tag_ids)) * 100.0
            
            # XỬ LÝ LOẠI 2: ĐỐI KHỚP THEO ĐIỂM PHỎNG VẤN CŨ (Interview Score)
            elif rule.rule_type == 'interview_score':
                # Giả định điểm tiềm năng lưu trên thang 100
                final_score = candidate.potential_score
                
            # XỬ LÝ LOẠI 3: CÁC TRƯỜNG HỢP KHÁC (MẶC ĐỊNH)
            else:
                final_score = 00.0
            
            # Khống chế điểm số trong khoảng từ 0% đến 100% và ghi nhận vào Database
            candidate.write({'match_score': min(max(final_score, 0.0), 100.0)})