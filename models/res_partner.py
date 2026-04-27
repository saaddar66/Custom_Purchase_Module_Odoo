# -*- coding: utf-8 -*-
from odoo import models, fields, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_rating = fields.Selection([
        ('1', 'Poor'),
        ('2', 'Average'),
        ('3', 'Excellent'),
    ], string="Vendor Rating", default='2')
    
    is_preferred_vendor = fields.Boolean(string="Preferred Vendor", default=False)
    
    payment_terms_override = fields.Many2one(
        'account.payment.term', 
        string="Payment Term Override",
        help="If set, this will override the default payment term on Purchase Orders."
    )
