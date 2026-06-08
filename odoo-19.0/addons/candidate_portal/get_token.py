#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('ODOO_ADDONS_PATH', os.path.join(os.path.dirname(__file__), 'addons'))

import odoo
from odoo import api, SUPERUSER_ID
from odoo.tools import config

# Connect to database
config['db_name'] = 'quoc'
config['db_user'] = 'quoc'
config['db_password'] = 'Admin123'

with odoo.api.Environment.manage():
    registry = odoo.registry('quoc')
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Find applicant
        applicant = env['hr.applicant'].search([('email_from', '=', 'quocdz0817@gmail.com')], limit=1)
        
        if applicant:
            # Generate token
            token_model = env['hr.candidate.portal.token']
            raw_token = token_model.generate_token(applicant.id)
            
            # Build URL
            base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
            login_url = f"{base_url}/candidate-portal/login?token={raw_token}"
            
            print(f"✅ Token: {raw_token}")
            print(f"✅ Login URL: {login_url}")
        else:
            print("❌ Applicant not found with email quocdz0817@gmail.com")
