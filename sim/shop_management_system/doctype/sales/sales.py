import frappe
from frappe.model.document import Document

class Sales(Document):
    def validate(self):
        total = 0
        for row in self.purchase:
            row.amount = row.qty * row.rate
            total += row.amount
        self.total_amount = total

@frappe.whitelist()
def submit_sales(name):
    try:
        doc = frappe.get_doc("Sales", name)
        if doc.docstatus == 0:
            doc.submit()
        return {"status": "success"}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Submit Sales Error")
        return {"status": "failed", "error": str(e)}
