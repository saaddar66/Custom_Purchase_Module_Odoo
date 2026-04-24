# -*- coding: utf-8 -*-
from odoo import models, fields, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    vendor_rating = fields.Selection([
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ], string="Vendor Rating", default='3')
    
    is_preferred_vendor = fields.Boolean(string="Preferred Vendor", default=False)
    
    payment_term_override = fields.Many2one(
        'account.payment.term', 
        string="Payment Term Override",
        help="If set, this will override the default payment term on Purchase Orders."
    )
