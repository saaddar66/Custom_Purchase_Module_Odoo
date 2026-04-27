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

### 2. Custom Fields & Vendor Management
- **Department & Requester:** Added `department_id` and `requested_by` fields securely linking to HR departments and standard internal users.
- **Advanced Priority System:** Overhauled the standard urgency selection to implement a custom 3-Star Priority rating system (*Normal/0-Star, Low/1-Star, Medium/2-Star, High/3-Star*) using Odoo's priority widget correctly with proper fallback (`ondelete`) rules.
- **Vendor Extensions:** Enhanced the `res.partner` model to include **Vendor Ratings** (1-5 Stars), a **Preferred Vendor** toggle, and a **Payment Term Override** for specific purchase automation.

### 3. Order Line Discounts
- Added a custom percentage-based `discount` field directly within the `purchase.order.line` items.
- Developed the Python calculation logic (`_compute_amount`) to appropriately recalculate the order line's total price, unit price, and subsequent taxes factoring in the newly applied discount.

### 4. Custom Interface & Odoo 18 Enhancements
- **View Inheritances:** Inherited and heavily customized both the standard `purchase.order.form` and `purchase.order.list` views.
- **Dynamic UX Row Coloring:** Configured Odoo 18 `list` views to apply specific conditional UI decorations (e.g., row colors turn red/danger when rejected, blue/info when pending).
- **Odoo 18 Syntactical Refinements:** Fixed deprecations regarding XPath queries by correctly switching old `<tree>` references to `<list>` formats, and simplified direct path targeting.

### 5. Advanced Reporting: Purchase Summary Report
The module includes a professional PDF **Purchase Summary Report** accessible directly from the "Print" menu on any Purchase Order. Key features include:
- **Comprehensive Header:** Displays vendor details, order date, and requester info.
- **Dynamic Status Tracking:** Clearly highlights the current approval state (Draft, Pending, Approved, Rejected).
- **Rejection Alerts:** Includes a prominent visual warning if the order was rejected by an approver.
- **Detailed Line Items:** Itemized table showing quantities, unit prices, and custom discounts.
- **Financial Breakdown:** Professional summary of untaxed amounts, taxes, and final totals.

### 6. Filtering & Search Enhancements
Improved the search experience within the Purchase module by adding:
- **Custom Filters:** One-click filters for "Pending Approval", "Approved", and "Rejected" states.
- **Date-Based Filtering:** Quick filters for "Orders Today" and "Orders This Month" using dynamic context evaluation.
- **Expanded Grouping:** Ability to group orders by Vendor, Approval Status, or Order Date.

### 7. Configuration Settings
Administrators can fine-tune module behavior via **Settings > Purchase > Purchase Automation & Logic**:
- **Approval Limit:** Set a monetary threshold. Orders exceeding this amount are automatically routed for approval.
- **Default Expense Account:** Define a global default account for purchase expenses.
- **Auto RFQ:** Toggle to enable/disable automated Request for Quotation generation based on stock procurement rules.

---

*This document serves as a tracking sheet for customizations successfully integrated into the module.*
