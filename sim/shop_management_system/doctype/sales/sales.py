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
                frappe.throw(f"Quantity must be greater than 0 for item")
            if not row.rate or row.rate <= 0:
                frappe.throw(f"Rate must be greater than 0 for item")

            row.amount = (row.qty or 0) * (row.rate or 0)
            total += row.amount

        self.total_amount = total

    def on_update_after_submit(self):
        self.validate()

@frappe.whitelist()
def edit_and_resubmit(docname, updated_items):
    print("updated_items:", updated_items)
    # """
    # Update Sales items (child table) in a submitted Sales document.
    # `updated_items` should be a list of dicts with keys: name, item, qty, rate.
    # """
    sales = frappe.get_doc('Sales', docname)
    if sales.docstatus != 1:
        frappe.throw(f"Sales document {docname} is not submitted.")

    if isinstance(updated_items, str):
        updated_items = frappe.parse_json(updated_items)

    for row in updated_items:
        if not row.get('item'):
            frappe.throw("Item is required for all rows.")
        if row.get('qty') is None or row.get('qty') <= 0:
            frappe.throw(f"Quantity for item must be greater than zero.")
        if row.get('rate') is None or row.get('rate') <= 0:
            frappe.throw(f"Rate for item must be greater than zero.")

            
    existing = {row.name for row in sales.get('purchase', [])}
    print("Existing items in Sales document:", existing)
    updated = set()
    print("Updated items to process:", updated_items)

    for row in updated_items:
        if "name" in row and row["name"] in existing:
            frappe.db.set_value("Sales Item", row["name"], {
                "item": row["item"],
                "qty": row["qty"],
                "rate": row["rate"],
                "amount": row["qty"] * row["rate"]
            })
            updated.add(row["name"])

        else:
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
            new_child.db_insert()
            updated.add(new_child.name)

    if updated:
        frappe.db.sql(
            """
            DELETE FROM `tabSales Item`
            WHERE parent = %(parent)s
              AND parenttype = 'Sales'
              AND parentfield = 'purchase'
              AND name NOT IN %(names)s
            """,
            {"parent": docname, "names": tuple(updated)}
        )
    else:
        frappe.db.sql(
            """
            DELETE FROM `tabSales Item`
            WHERE parent = %(parent)s
              AND parenttype = 'Sales'
              AND parentfield = 'purchase'
            """,
            {"parent": docname}
        )
    sales.reload()
    total = 0
    for row in sales.get("purchase", []):
        total += row.amount
    frappe.db.set_value("Sales", docname, "total_amount", total)
    # sales.save()  
    frappe.db.commit() 
    frappe.msgprint(f"Sales document {docname} updated successfully.")
