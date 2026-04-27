from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Extend the existing 'state' field selection
    state = fields.Selection(selection_add=[
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], ondelete={'pending': 'set default', 'approved': 'set default', 'rejected': 'set default'})

    # Add new fields
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user)
    department_id = fields.Many2one('hr.department', string="Department")
    priority = fields.Selection(selection_add=[
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High')
    ], ondelete={'0': 'set default', '1': 'set default', '2': 'set default', '3': 'set default'})

    rejection_reason = fields.Text(string="Rejection Reason")

    @api.model
    def _get_default_expense_account(self):
        """Safely retrieve the configured expense account as a recordset."""
        account_id = self.env['ir.config_parameter'].sudo().get_param('custom_purchase.default_expense_account_id')
        if account_id:
            return self.env['account.account'].browse(int(account_id))
        return self.env['account.account']

    def action_submit_for_approval(self):
        """Logic to check limit and change state"""
        # We fetch the limit from configuration (Settings)
        limit_str = self.env['ir.config_parameter'].sudo().get_param('custom_purchase.approval_limit', '0.0')
        limit = float(limit_str) if limit_str else 0.0
        
        for order in self:
            if order.amount_total > limit:
                order.state = 'pending'
            else:
                # If below limit, bypass and use Odoo's standard confirm
                order.button_confirm()

    def action_approve(self):
        # Security check: Only users in the 'Approver' group can click this
        if not self.env.user.has_group('custom_purchase_module.group_purchase_approver'):
            raise UserError(_("You do not have permission to approve this order."))
        self.write({'state': 'approved'})
        return self.button_confirm() # Call standard Odoo confirmation

    def action_reject(self):
        # Only users in the 'Approver' group can click this
        if not self.env.user.has_group('custom_purchase_module.group_purchase_approver'):
            raise UserError(_("You do not have permission to reject this order."))
        
        for order in self:
            if not order.rejection_reason:
                raise UserError(_("Please provide a rejection reason."))
            order.state = 'rejected'


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float(string="Discount (%)", digits='Discount', default=0.0)

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        for line in self:
            # Calculate the discounted unit price
            discount_factor = 1 - (line.discount or 0.0) / 100.0
            discounted_price = line.price_unit * discount_factor
            
            # Compute taxes based on the discounted price
            taxes = line.taxes_id.compute_all(
                discounted_price, 
                line.order_id.currency_id, 
                line.product_qty, 
                product=line.product_id, 
                partner=line.order_id.partner_id
            )
            
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })