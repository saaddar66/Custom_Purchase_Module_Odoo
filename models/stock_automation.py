# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _select_seller(self, partner_id=False, quantity=0.0, date=False, uom_id=False, params=False):
        """
        Override to implement 'Best Vendor' logic based on rating and price.
        Only applied if 'Auto RFQ' is enabled in settings.
        """
        res = super()._select_seller(partner_id=partner_id, quantity=quantity, date=date, uom_id=uom_id, params=params)
        
        # If a specific partner is requested, stick to standard Odoo behavior
        if partner_id:
            return res

        # Check if custom Best Vendor logic is enabled
        auto_rfq = self.env['ir.config_parameter'].sudo().get_param('custom_purchase.auto_rfq')
        if not auto_rfq:
            return res

        sellers = self.seller_ids.filtered(lambda s: 
            (not s.company_id or s.company_id == self.env.company) and 
            (not date or (s.date_start or fields.Date.min) <= date <= (s.date_end or fields.Date.max))
        )
        
        if sellers:
            # Sort logic: 
            # 1. Vendor Rating (Higher is better: 3 > 2 > 1)
            # 2. Price (Lower is better)
            # We use a negative price for reverse sorting to get lowest price
            sorted_sellers = sellers.sorted(
                key=lambda s: (int(s.partner_id.vendor_rating or 0), -s.price),
                reverse=True
            )
            return sorted_sellers[0]
            
        return res

class Orderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def _prepare_procurement_values(self, date_planned=False, group_id=False):
        """
        Ensure procurement values include our custom logic or triggers.
        """
        values = super()._prepare_procurement_values(date_planned=date_planned, group_id=group_id)
        # We can inject additional context here if needed for the PO creation
        return values
