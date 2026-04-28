from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

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

    @api.onchange('partner_id')
    def _onchange_partner_id_vendor_check(self):
        """
        Learning Exercise: Business Logic on Vendor selection.
        - Triggers a warning for low-rated vendors.
        - Applies defaults or logs for preferred vendors.
        """
        if not self.partner_id:
            return

        # 1. Warning for Low Rating
        if self.partner_id.vendor_rating == '1':
            return {
                'warning': {
                    'title': _("Low Vendor Rating"),
                    'message': _("Warning: This vendor has a low rating. Please proceed with caution."),
                }
            }

        # 2. Logic for Preferred Vendors
        if self.partner_id.is_preferred_vendor:
            # We can set a default note or just log for the exercise
            self.notes = _("Note: This is one of our Preferred Vendors.")
            # Simple console log as requested
            print(f"DEBUG: Preferred Vendor {self.partner_id.name} selected.")

    @api.model
    def _get_default_expense_account(self):
        """Safely retrieve the configured expense account as a recordset."""
        account_id = self.env['ir.config_parameter'].sudo().get_param('custom_purchase.expense_account_id')
        if account_id:
            return self.env['account.account'].browse(int(account_id))
        return self.env['account.account']

    def action_submit_for_approval(self):
        """
        Logic to check limit and change state.
        Learning Point: Using ir.config_parameter.
        - 'ir.config_parameter' is a global key-value store for Odoo settings.
        - We use .sudo() because regular users might not have access to read 
          system parameters, but the system logic needs to verify the limit.
        """
        # Fetch the limit from System Parameters (defined in res.config.settings)
        # The key must match the 'config_parameter' defined in the model field.
        limit_str = self.env['ir.config_parameter'].sudo().get_param('custom_purchase.approval_limit', default='0.0')
        limit = float(limit_str) if limit_str else 0.0
        
        for order in self:
            if order.amount_total > limit:
                # If the order exceeds the limit, move to 'Pending'
                order.state = 'pending'
            else:
                # If below limit, bypass approval and confirm directly
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

    @api.model
    def _cron_reminder_pending_approval(self):
        """
        Find orders in 'Pending Approval' for more than 3 days 
        and send a reminder message to the Approvers group.
        """
        three_days_ago = fields.Datetime.now() - relativedelta(days=3)
        pending_orders = self.search([
            ('state', '=', 'pending'),
            ('create_date', '<=', three_days_ago)
        ])
        
        if pending_orders:
            # Retrieve the Approver group
            approver_group = self.env.ref('custom_purchase_module.group_purchase_approver')
            approvers = approver_group.users
            
            for order in pending_orders:
                # Post a message on the chatter to notify approvers
                order.message_post(
                    body=_("Reminder: This Purchase Order #%s has been pending for over 3 days. Please review.") % order.name,
                    partner_ids=approvers.partner_id.ids
                )
                # Simple console log for visibility during tests
                print(f"DEBUG: Sent reminder for {order.name} to {len(approvers)} approvers.")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float(string="Discount (%)", digits='Discount', default=0.0)
    x_tax_override = fields.Boolean(string="Override Taxes", default=False)
    x_custom_tax_ids = fields.Many2many('account.tax', string="Custom Taxes")
    x_account_id = fields.Many2one('account.account', string="Expense Account")

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount', 'x_tax_override', 'x_custom_tax_ids')
    def _compute_amount(self):
        for line in self:
            # Logic for Tax Override
            taxes = line.x_custom_tax_ids if line.x_tax_override else line.taxes_id
            
            # Calculate the discounted unit price
            discount_factor = 1 - (line.discount or 0.0) / 100.0
            discounted_price = line.price_unit * discount_factor
            
            # Compute taxes based on the discounted price or override
            res = taxes.compute_all(
                discounted_price, 
                line.order_id.currency_id, 
                line.product_qty, 
                product=line.product_id, 
                partner=line.order_id.partner_id
            )
            
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in res.get('taxes', [])),
                'price_total': res['total_included'],
                'price_subtotal': res['total_excluded'],
            })

    @api.constrains('price_unit')
    def _check_price_zero_fallback(self):
        """Logic for Price = 0 Fallback Account Assignment."""
        for line in self:
            if line.price_unit == 0:
                account_id = self.env['ir.config_parameter'].sudo().get_param('custom_purchase.expense_account_id')
                if account_id:
                    line.x_account_id = int(account_id)

    def _prepare_account_move_line(self, move=False):
        """Override to pass the custom account to the Bill if price is 0 or manual."""
        res = super()._prepare_account_move_line(move=move)
        if self.x_account_id:
            res.update({'account_id': self.x_account_id.id})
        return res