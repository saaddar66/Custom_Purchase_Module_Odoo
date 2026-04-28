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

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        """
        Integration Fix: Inventory Validation.
        Prevent validating a receipt if the quantity significantly exceeds 
        the Purchase Order quantity (10% tolerance).
        """
        for move in self:
            if move.purchase_line_id:
                # Calculate the maximum allowed quantity (110% of PO qty)
                po_qty = move.purchase_line_id.product_qty
                max_allowed = po_qty * 1.1
                
                # In Odoo 18, 'quantity' field on stock.move represents the 'Done' quantity
                if move.quantity > max_allowed:
                    raise UserError(_(
                        "Receipt Validation Error: The quantity for '%s' (%s) exceeds "
                        "the Purchase Order quantity (%s) by more than the allowed 10%% tolerance. "
                        "Please adjust the receipt or update the Purchase Order first."
                    ) % (move.product_id.display_name, move.quantity, po_qty))
        
        return super()._action_done(cancel_backorder=cancel_backorder)
