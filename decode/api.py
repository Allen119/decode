import frappe
import hashlib
from frappe import _

x = None 
@frappe.whitelist(allow_guest=True)
def register_user(full_name, email, password):
    try:
        # Validate inputs
        if not full_name or not email or not password:
            return {"message": "All fields are required."}
        
        # Check if email already exists
        if frappe.db.exists("user_reg", {"email": email}):
            return {"message": "Email already registered."}
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Create a new User Registration document
        user_doc = frappe.get_doc({
            "doctype": "user_reg",
            "fullname": full_name,
            "email": email,
            "password": hashed_password
        })
        user_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Return success message
        return {"message": "Registration successful!", "name": user_doc.name}
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Register User Error")
        return {"message": f"An error occurred: {str(e)}"}

@frappe.whitelist(allow_guest=True)
def login_user(email, password):
    global x
    try:
        # Retrieve the full user document
        user_doc = frappe.get_doc("user_reg", {"email": email})
        
        if not user_doc:
            return {"message": "User with this email does not exist."}
        
        # Hash the input password
        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Directly access the password field from the document
        stored_password = user_doc.get("password")
        
        # Compare hashed passwords
        if stored_password != hashed_input_password:
            return {
                "message": "Invalid password.",
                "stored_password": stored_password,
                "input_password": hashed_input_password
            }
        
        x = user_doc.name

        return {
            "message": "Login successful!",
            "user": user_doc.name,
            "stored_password": stored_password,
            "input_password": hashed_input_password
        }
    
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Login User Error")
        return {"message": f"An error occurred: {str(e)}"}

@frappe.whitelist(allow_guest=True)
def codingFiles(file_name, code, language):
    global x
    try:
        # Set the user ID to 9 (this should be dynamic if needed)
        user_id = x
        # Fetch the User document from the 'user_reg' DocType
        user = frappe.get_doc("user_reg", user_id)

        # Check if the child table exists
        if not hasattr(user, "codingfiles"):
            return {"message": f"Child table 'codingFiles' does not exist in the User document.", "user": user.as_dict()}

        # Check if the file already exists in the child table
        existing_file = next((file for file in user.codingfiles if file.filename == file_name), None)

        if existing_file:
            return {"message": f"File '{file_name}' already exists and will not be saved again.", "user": user.as_dict()}

        # Append the new file to the Coding Files child table
        user.append("codingfiles", {
            "filename": file_name,
            "language": language,
            "code": code,
        })

        # Save the User document to commit the changes
        user.save()

        # Return the user document along with the result
        return {
            "message": f"File '{file_name}' saved successfully for user {user_id}.",
            "user": user.as_dict()  # Always include the user document
        }
    
    except frappe.DoesNotExistError:
        # Handle the case where the user does not exist
        return {"message": f"User with ID {user_id} does not exist.", "user": None}
    
    except Exception as e:
        # Log any other errors
        frappe.log_error(frappe.get_traceback(), "Coding Files Error")
        return {"message": f"An error occurred: {str(e)}", "user": None}

@frappe.whitelist(allow_guest=True)
def getfiles(search_uuid):
    global x
    try:
        
        user_id = "0194adcf-15b7-7d81-a641-fc497681d666"
        # Fetch the user document using the provided user_id (UUID)
        user = frappe.get_doc("user_reg", user_id)

        # Check if the user has files in the 'codingfiles' child table
        if not user.codingfiles:
            return {
                "message": f"No files found for user {user_id}.",
                "file": None
            }

        # Search for the file by UUID in the user's 'codingfiles' child table
        for file_entry in user.codingfiles:
            if file_entry.name == search_uuid:
                # File found, return its details
                return {
                    "message": f"File with UUID {search_uuid} found",
                    "file": {
                        "filename": file_entry.filename,
                        "language": file_entry.language,
                        "code": file_entry.code,
                        "uuid": file_entry.name,
                        "creation": file_entry.creation,
                        "modified": file_entry.modified,
                        "owner": file_entry.owner
                    }
                }

        # If no file was found for this user
        return {
            "message": f"File with UUID {search_uuid} not found for user {user_id}.",
            "file": None
        }

    except frappe.DoesNotExistError:
        return {
            "message": f"Error: User with UUID {user_id} does not exist.",
            "file": None
        }
    except Exception as e:
        # Log any other errors
        frappe.log_error(frappe.get_traceback(), "Get File by UUID Error")
        return {
            "message": f"An error occurred: {str(e)}",
            "file": None
        }

@frappe.whitelist(allow_guest=True)
def updatecode(file_uuid, code):
    try:
        frappe.logger().info(f"Guest user attempting to update file: {file_uuid}")
        user_id = "0194adcf-15b7-7d81-a641-fc497681d666"  # Example user ID
        
        # Sanitize and validate inputs
        if not file_uuid or not code:
            return {
                "status": "error",
                "message": "File UUID and code are required"
            }
            
        user = frappe.get_doc("user_reg", user_id)
        frappe.logger().info(f"User document fetched: {user.name}")
        
        file_entry = None
        for entry in user.codingfiles:
            if entry.name == file_uuid:
                file_entry = entry
                break
                
        if file_entry:
            frappe.logger().info(f"File found: {file_uuid}")
            file_entry.code = code
            user.save()
            frappe.logger().info(f"File updated successfully: {file_uuid}")
            
            response = {
                "status": "success",
                "message": "File updated successfully",
                "file": {
                    "filename": file_entry.filename,
                    "language": file_entry.language,
                    "code": file_entry.code,
                    "uuid": file_entry.name,
                    "creation": str(file_entry.creation),
                    "modified": str(file_entry.modified),
                    "owner": file_entry.owner
                }
            }
            
            return response
            
        else:
            frappe.logger().error(f"File not found: {file_uuid}")
            return {
                "status": "error",
                "message": f"File with UUID {file_uuid} not found"
            }
            
    except Exception as e:
        frappe.logger().error(f"Error in updatecode: {str(e)}")
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }
