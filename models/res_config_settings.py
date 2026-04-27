# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_approval_limit = fields.Float(
        string="Purchase Approval Limit",
        config_parameter='custom_purchase.approval_limit',
        default=0.0,
        help="Minimum amount required for a Purchase Order to require approval."
    )
    
    purchase_expense_account_id = fields.Many2one(
        'account.account',
        string="Default Expense Account",
        config_parameter='custom_purchase.expense_account_id',
        help="Default account to use for expenses on purchase orders."
    )
    
    auto_rfq = fields.Boolean(
        string="Auto RFQ",
        config_parameter='custom_purchase.auto_rfq',
        default=False,
        help="Automatically generate RFQs based on stock logic."
    )
