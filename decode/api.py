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
    if x is None:
        return {"message": "You should log in first.", "file": None}

    try:       
        # Step 1: Get all users
        all_users = frappe.get_all("user_reg", fields=["name"])
        users_with_coding_files = []  # List to store user names who have coding files
        
        # Step 2: Loop through all users and check if they have coding files
        for user in all_users:
            user_doc = frappe.get_doc("user_reg", user.name)  # Fetch full user document
            
            if user_doc.codingfiles:  # Check if codingfiles table has entries
                users_with_coding_files.append(user.name)  # Store only user name
        
        # Step 3: Loop through the users with coding files and search for the file
        for user_name in users_with_coding_files:
            user_doc = frappe.get_doc("user_reg", user_name)  # Fetch full user document

            # Step 4: Search for the file by UUID in the user's 'codingfiles' child table
            for file_entry in user_doc.codingfiles:
                if file_entry.name == search_uuid:
                    # File found, return its details
                    return {
                        "message": f"File with UUID {search_uuid} found for user {user_name}",
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

        # If no file was found for any user
        return {
            "message": f"File with UUID {search_uuid} not found for any user.",
            "file": None
        }

    except frappe.DoesNotExistError:
        return {
            "message": f"Error: User with UUID does not exist.",
            "file": None
        }
    except Exception as e:
        # Log any other errors
        frappe.log_error(frappe.get_traceback(), "Get File by UUID Error")
        return {
            "message": f"An error occurred: {str(e)}",
            "file": None
        }


import frappe
from frappe import publish_realtime

@frappe.whitelist(allow_guest=True)
def update_code(file_uuid, code):
    """Update code and broadcast changes to all connected clients"""
    try:
        result = save_code_to_database(file_uuid, code)
        
        if result["status"] == "success":
            # Log before broadcasting
            print(f"Broadcasting code update for file: {file_uuid}")
            frappe.logger().debug(f"Broadcasting code update - File UUID: {file_uuid}")
            
            message = {
                "file_uuid": file_uuid,
                "code": code,
                "modified": result["file"]["modified"]
            }
            
            # Broadcast the update
            publish_realtime(
                event="code_update",
                message=message,
                user="all"
            )
            
            # Ensure result["message"] is a dictionary before modifying it
            if isinstance(result["message"], str):
                result["message"] = {"text": result["message"]}  # Convert string to dictionary
            
            result["message"]["websocket_broadcast"] = True  # Now it's safe to add

            # Log the broadcast
            print(f"Broadcast completed for file: {file_uuid}")
            frappe.logger().debug(f"Code update broadcast completed for file: {file_uuid}")
            
        return result

    except Exception as e:
        error_msg = f"Update Code Error: {str(e)}"
        print(error_msg)
        frappe.logger().error(error_msg)
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }

def save_code_to_database(file_uuid, code):
    """Helper function to save code to database"""
    all_users = frappe.get_all("user_reg", fields=["name"])
    users_with_coding_files = []
    
    for user in all_users:
        user_doc = frappe.get_doc("user_reg", user.name)
        if user_doc.codingfiles:
            users_with_coding_files.append(user.name)
    
    for user_name in users_with_coding_files:
        user_doc = frappe.get_doc("user_reg", user_name)
        
        for file_entry in user_doc.codingfiles:
            if file_entry.name == file_uuid:
                file_entry.code = code
                user_doc.save()
                
                return {
                    "status": "success",
                    "message": {  # Ensure message is a dictionary
                        "text": f"File {file_uuid} updated successfully"
                    },
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
    
    return {
        "status": "error",
        "message": {  # Ensure message is a dictionary
            "text": f"File with UUID {file_uuid} not found"
        }
    }


import subprocess
@frappe.whitelist(allow_guest=True)
def execute(code):
    try:
        frappe.logger().info(f"Executing Code:\n{code}")

        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout
        error = result.stderr

        frappe.logger().info(f"Execution Output:\n{output}")
        frappe.logger().info(f"Execution Error:\n{error}")

        return {"output": output, "error": error}

    except subprocess.TimeoutExpired:
        frappe.logger().error("Execution timed out.")
        return {"error": "Execution timed out."}
    except Exception as e:
        frappe.logger().error(f"Execution failed: {str(e)}")
        return {"error": str(e)}
    
    

@frappe.whitelist(allow_guest=True)
def findbyuuid(uuid):
    # Get all user_reg documents
    all_users = frappe.get_all("user_reg", fields=["name"])

    # Loop through each user and check their codingfiles
    for user in all_users:
        # Fetch the user document
        user_doc = frappe.get_doc("user_reg", user.name)
        
        # Check if the user has any codingfiles in the child table
        if user_doc.codingfiles:
            # Loop through each coding file and check if the file matches the given UUID
            for codingfile in user_doc.codingfiles:
                if codingfile.name == uuid:  # Compare with the provided uuid
                    # Return the found file details as a dictionary
                    return uuid# This will return the file details codingfile.as_dict()
    # If file is not found, return a message
    return _(False)

import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_user_fullname():
    global x
    user_id = x
    fullname = frappe.get_value("user_reg", user_id, "fullname")

    if fullname:
        return {"fullname": fullname}
    else:
        return {"error": _("User not found.")}
