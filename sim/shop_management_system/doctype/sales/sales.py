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

    
    frappe.db.set_value("Sales", docname, "total_amount", total_amount)
    # sales.save()  
    frappe.db.commit() 
    frappe.msgprint(f"Sales document {docname} updated successfully.")




# import frappe
# import json
# from frappe.model.document import Document

# class Sales(Document):
#     def validate(self):
#         if not self.purchase or len(self.purchase) == 0:
#             frappe.throw("At least one item must be added to the purchase table.")

#         total = 0
#         for row in self.purchase:
#             if not row.item:
#                 frappe.throw("Item name cannot be empty in the purchase table.")
#             if not row.qty or row.qty <= 0:
#                 frappe.throw(f"Quantity must be greater than 0 for item: {row.item}")
#             if row.rate is None or row.rate <= 0:
#                 frappe.throw(f"Rate must be greater than 0 for item: {row.item}")

#             row.amount = row.qty * row.rate
#             total += row.amount

#         self.total_amount = total

#     def on_update_after_submit(self):
#         self.validate()

# @frappe.whitelist()
# def edit_and_resubmit(docname, updated_items):
#     """
#     Update child rows in a submitted Sales doc and recalc total_amount via SQL.
#     updated_items: list of dicts with keys name, item, qty, rate.
#     """
#     # 1. Load document and parse data
#     sales = frappe.get_doc('Sales', docname)
#     if sales.docstatus != 1:
#         frappe.throw(f"Sales document {docname} is not submitted.")

#     if isinstance(updated_items, str):
#         updated_items = frappe.parse_json(updated_items)

#     if not updated_items:
#         frappe.throw("No items provided for update.")

#     # 2. Prepare sets for existing and updated row names
#     existing_names = {row.name for row in sales.purchase}
#     updated_names = set()

#     # 3. Process each incoming row
#     for row in updated_items:
#         item, qty, rate = row['item'], row['qty'], row['rate']
#         # Validate
#         if not item:
#             frappe.throw("Item is required.")
#         if qty <= 0:
#             frappe.throw(f"Quantity must be > 0 for item: {item}")
#         if rate <= 0:
#             frappe.throw(f"Rate must be > 0 for item: {item}")

#         amount = qty * rate

#         if row.get('name') in existing_names:
#             # 3a. Update existing child via SQL
#             frappe.db.set_value('Sales Item', row['name'], {
#                 'item': item,
#                 'qty': qty,
#                 'rate': rate,
#                 'amount': amount
#             })
#             updated_names.add(row['name'])
#         else:
#             # 3b. Insert new child row
#             frappe.get_doc({
#                 'doctype': 'Sales Item',
#                 'parent': docname,
#                 'parentfield': 'purchase',
#                 'parenttype': 'Sales',
#                 'item': item,
#                 'qty': qty,
#                 'rate': rate,
#                 'amount': amount
#             }).db_insert()
#             new_name = frappe.db.get_last_doc('Sales Item').name
#             updated_names.add(new_name)

# removed = existing_names - updated_names
# for name in removed:
#     frappe.delete_doc("Sales Item", name, force=True)

#     frappe.db.sql(
#         """
#         UPDATE `tabSales`
#         SET total_amount = (
#           SELECT COALESCE(SUM(amount),0)
#           FROM `tabSales Item`
#           WHERE parent=%(parent)s
#             AND parenttype='Sales'
#             AND parentfield='purchase'
#         )
#         WHERE name=%(parent)s
#         """,
#         {'parent': docname}
#     )

#     frappe.db.commit()
#     return {'status': 'success', 'message': 'Items updated and total_amount recalculated.'}