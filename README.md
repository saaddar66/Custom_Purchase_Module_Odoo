# Custom Purchase Module for Odoo 18

This repository contains a custom module developed for Odoo 18 that extends and enhances the standard purchase module functionality. It adds robust approval workflows, discounting capabilities, and advanced user interface customizations.

## Tasks Completed & Features Implemented

Here is a summary of all the key development tasks accomplished in this module so far:

### 1. Purchase Approval Workflow
- **Multi-Level States:** Extended the default purchase order states to include `Pending Approval`, `Approved`, and `Rejected`.
- **Approval Limit Logic:** Added dynamic logic allowing purchase orders above a configured limit to be routed to "Pending Approval", rather than directly confirming them.
- **Action Buttons:** Added interactive buttons (`Submit for Approval`, `Approve`, `Reject`) on the Purchase Order form view with smart visibility tracking based on the order's state.
- **Rejection Tracking:** Created a dedicated "Approval Information" notebook tab to store and display specific Rejection Reasons, which are structurally mandated when rejecting a purchase order.
- **Access Rights / Security:** Restricted `Approve` and `Reject` actions exclusively to users belonging to the custom `group_purchase_approver` security group.

### 2. Purchase Order Custom Fields
- **Department & Requester:** Added `department_id` and `requested_by` fields securely linking to HR departments and standard internal users.
- **Advanced Priority System:** Overhauled the standard urgency selection to implement a custom 3-Star Priority rating system (*Normal/0-Star, Low/1-Star, Medium/2-Star, High/3-Star*) using Odoo's priority widget correctly with proper fallback (`ondelete`) rules.

### 3. Order Line Discounts
- Added a custom percentage-based `discount` field directly within the `purchase.order.line` items.
- Developed the Python calculation logic (`_compute_amount`) to appropriately recalculate the order line's total price, unit price, and subsequent taxes factoring in the newly applied discount.

### 4. Custom Interface & Odoo 18 Enhancements
- **View Inheritances:** Inherited and heavily customized both the standard `purchase.order.form` and `purchase.order.list` views.
- **Dynamic UX Row Coloring:** Configured Odoo 18 `list` views to apply specific conditional UI decorations (e.g., row colors turn red/danger when rejected, blue/info when pending).
- **Odoo 18 Syntactical Refinements:** Fixed deprecations regarding XPath queries by correctly switching old `<tree>` references to `<list>` formats, and simplified direct path targeting.

---

*This document serves as a tracking sheet for customizations successfully integrated into the module.*
