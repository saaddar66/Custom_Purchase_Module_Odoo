# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    approval_limit = fields.Float(
        string="Approval Limit",
        config_parameter='custom_purchase.approval_limit',
        default=0.0,
        help="Purchase orders with amount total greater than this will require approval."
    )

    # Note: Using config_parameter directly in the field definition 
    # removes the need for manual get_values/set_values in modern Odoo.
