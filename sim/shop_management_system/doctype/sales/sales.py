import frappe
import json
from frappe.model.document import Document

class Sales(Document):
    def validate(self):
        if not self.purchase or len(self.purchase) == 0:
            frappe.throw("At least one item must be added to the purchase table.")

        total = 0
        for row in self.purchase:
            if not row.item:
                frappe.throw("Item name cannot be empty in the purchase table.")
            if not row.qty or row.qty <= 0:
                frappe.throw(f"Quantity must be greater than 0 for item: {row.item or '[Blank Item]'}")

            row.amount = (row.qty or 0) * (row.rate or 0)
            total += row.amount

        self.total_amount = total

    def on_update_after_submit(self):
        self.validate()

@frappe.whitelist()
def edit_and_resubmit(docname, updated_items):
    """
    Update Sales items (child table) in a submitted Sales document.
    `updated_items` should be a list of dicts with keys: name, item, qty, rate.
    """
    # Get the submitted Sales document
    sales = frappe.get_doc('Sales', docname)
    if sales.docstatus != 1:
        frappe.throw(f"Sales document {docname} is not submitted.")

    # Parse items (in case it's a JSON string)
    if isinstance(updated_items, str):
        updated_items = frappe.parse_json(updated_items)

    # Validate incoming items
    for row in updated_items:
        if not row.get('item'):
            frappe.throw("Item is required for all rows.")
        if row.get('qty') is None or row.get('qty') <= 0:
            frappe.throw(f"Quantity for item {row.get('item')} must be greater than zero.")

    # Collect existing child row names
    existing_names = {row.name for row in sales.get('purchase', [])}
    updated_names = set()

    # Update or insert each row from dialog
    for row in updated_items:
        row_name = row.get('name')
        amount = row['qty'] * row['rate']
        if row_name and row_name in existing_names:
            # Update existing child row
            child = frappe.get_doc("Sales Item", row_name)
            child.item = row['item']
            child.qty = row['qty']
            child.rate = row['rate']
            child.amount = amount
            child.db_update()  # bypasses validation
            updated_names.add(row_name)
        else:
            # Insert new child row
            new_child = frappe.get_doc({
                "doctype": "Sales Item",
                "parent": docname,
                "parentfield": "purchase",
                "parenttype": "Sales",
                "item": row['item'],
                "qty": row['qty'],
                "rate": row['rate'],
                "amount": amount
            })
            new_child.db_insert()  # bypasses validation
            updated_names.add(new_child.name)

        # Delete any removed rows in a single SQL statement (no additional loop)
    if updated_names:
        frappe.db.sql(
            """
            DELETE FROM `tabSales Item`
            WHERE parent = %(parent)s
              AND parenttype = 'Sales'
              AND parentfield = 'purchase'
              AND name NOT IN %(names)s
            """,
            {"parent": docname, "names": tuple(updated_names)}
        )
    else:
        # If no updated rows, delete all rows for this Sales
        frappe.db.sql(
            """
            DELETE FROM `tabSales Item`
            WHERE parent = %(parent)s
              AND parenttype = 'Sales'
              AND parentfield = 'purchase'
            """,
            {"parent": docname}
        )

    # Update total_amount field on Sales("Sales", docname, "total_amount", total)  # update parent doc

    # Commit the changes
    frappe.db.commit()  # save all updates

    return {"status": "success", "message": "Items updated"}
