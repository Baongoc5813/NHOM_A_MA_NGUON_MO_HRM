#!/usr/bin/env python
import os
import sys
os.environ['ODOO_RC'] = 'd:/odoo/odoo/odoo/.odoorc'
sys.path.insert(0, 'd:/odoo/odoo')

import odoo
from odoo import api, SUPERUSER_ID
from datetime import datetime

# Connect to Odoo
registry = odoo.registry('quoc')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Get applicant
    applicant = env['hr.applicant'].search([('email_from', '=', 'quocdz0817@gmail.com')], limit=1)
    if applicant:
        # Generate token
        raw_token = env['hr.candidate.portal.token'].generate_token(applicant.id)
        base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')
        login_url = f"{base_url}/candidate-portal/login?token={raw_token}"
        
        print(f"\n✓ Token Generated:")
        print(f"  Raw Token: {raw_token}")
        print(f"  Login URL: {login_url}")
        print(f"  Time: {datetime.now()}")
        print(f"  Applicant: {applicant.partner_name}")
    else:
        print("✗ Applicant not found")
