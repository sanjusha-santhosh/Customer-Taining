from frappe.model.document import Document
from frappe.utils import add_days, date_diff, getdate
import frappe

class CustomerTrainingLog(Document):
    def before_insert(self):
        self.training_id = frappe.model.naming.make_autoname("CTL-.#####")

    def validate(self):
        self.set_duration()
        self.set_feedback_due_date()
        self.check_duplicate_log()

    def set_duration(self):
        if self.start_date and self.end_date:
            self.duration_days = date_diff(self.end_date, self.start_date)

    def set_feedback_due_date(self):
        if self.end_date and self.training_type:
            feedback_days = {"Basic": 7, "Advanced": 14, "Special": 21}.get(self.training_type)
            if feedback_days:
                self.feedback_due_date = add_days(self.end_date, feedback_days)

    def check_duplicate_log(self):
        if not self.customer or not self.training_type or not self.start_date:
            return

        month = getdate(self.start_date).month
        year = getdate(self.start_date).year

        existing = frappe.db.exists(
            "Customer Training Log",
            {
                "customer": self.customer,
                "training_type": self.training_type,
                "start_date": ["between", [f"{year}-{month:02d}-01", f"{year}-{month:02d}-31"]],
                "name": ["!=", self.name]
            }
        )
        if existing:
            frappe.throw("A training log for this customer and type already exists in the same month.")
