import frappe
from frappe.model.document import Document
import json


class Sales(Document):
    def validate(self):
        total = 0
        for row in self.purchase:
            row.amount = (row.qty or 0) * (row.rate or 0)
            total += row.amount
        self.total_amount = total

    def on_update_after_submit(self):
        frappe.db.set_value(self.doctype, self.name, 'status', 'Submitted')
        total = 0
        for row in self.purchase:
            row.amount = (row.qty or 0) * (row.rate or 0)
            total += row.amount
        self.total_amount = total

@frappe.whitelist()
def edit_and_resubmit(docname, sales_items):
    sales_items = json.loads(sales_items)
    doc = frappe.get_doc("Sales", docname)

    frappe.db.delete("Sales Item", {"parent": doc.name})

    total_amount = 0
    for row in sales_items:
        amount = (row.get("qty") or 0) * (row.get("rate") or 0)
        total_amount += amount

        frappe.get_doc({
            "doctype": "Sales Item",
            "parent": doc.name,
            "parenttype": "Sales",
            "parentfield": "purchase",
            "item": row.get("item"),
            "qty": row.get("qty"),
            "rate": row.get("rate"),
            "amount": amount
        }).db_insert()

    frappe.db.set_value("Sales", docname, {"total_amount": total_amount})