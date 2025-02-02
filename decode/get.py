import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_all_user_registrations():
    # Fetch all User Registration documents
    user_docs = frappe.get_all("user_reg", fields=["fullname", "email", "password"])

    # If no user registrations are found
    if not user_docs:
        return {"message": "No user registrations found."}

    # Return the list of all user registrations
    return {"users": user_docs}

