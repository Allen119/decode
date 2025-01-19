import frappe

@frappe.whitelist(allow_guest=True)
def register_user(full_name, email, password):
    try:
        # Validate inputs
        if not full_name or not email or not password:
            return {"message": "All fields are required."}

        # Check if email already exists
        if frappe.db.exists("user_reg", {"email": email}):  # Correct DocType name
            return {"message": "Email already registered."}

        # Create a new User Registration document
        user_doc = frappe.get_doc({
            "doctype": "user_reg",  # Correct DocType name
            "fullname": full_name,
            "email": email,
            "password": password
        })
        user_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Return success message
        return {"message": "Registration successful!", "name": user_doc.name}

    except Exception as e:
        # Log the error
        frappe.log_error(frappe.get_traceback(), "Register User Error")
        return {"message": f"An error occurred: {str(e)}"}