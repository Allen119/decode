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


from frappe import publish_realtime
@frappe.whitelist(allow_guest=True)
def update_code(file_uuid, code):
    """Update code and broadcast changes to all connected clients."""
    try:
        # Log incoming request with truncated code for readability
        frappe.logger().debug(f"📩 Received update for file: {file_uuid}, code length: {len(code)}")
        print(f"📩 Received update for file: {file_uuid}, code length: {len(code)}")
        
        result = save_code_to_database(file_uuid, code)
        
        if result.get("status") == "success":
            message = {
                "file_uuid": file_uuid,
                "content": code,
                "modified": result["file"]["modified"],
                "broadcast_id": frappe.utils.random_string(8)  # Add unique ID to track broadcast
            }
            
            # Enhanced logging
            frappe.logger().debug(f"📡 Broadcasting update with ID {message['broadcast_id']} for file: {file_uuid}")
            print(f"📡 Broadcasting update with ID {message['broadcast_id']} for file: {file_uuid}")
            
            # Broadcast to all clients
            publish_realtime(
                event="code_update",
                message=message
            )
            
            # Log after broadcast attempt
            print(f"✅ Completed broadcast attempt for ID {message['broadcast_id']}")
            frappe.logger().debug(f"Broadcast completed for ID {message['broadcast_id']}")
            
            if isinstance(result["message"], str):
                result["message"] = {"text": result["message"]}
                
            result["message"]["websocket_broadcast"] = True
            result["message"]["broadcast_id"] = message["broadcast_id"]
            return result
            
        return result  # file not found or other error
        
    except Exception as e:
        error_msg = f"❌ Update Code Error: {str(e)}"
        frappe.logger().error(error_msg)
        print(error_msg)
        return {
            "status": "error",
            "message": {"text": f"An error occurred: {str(e)}"}
        }

def save_code_to_database(file_uuid, code):
    """Save code to user_reg.codingfiles where UUID matches."""
    all_users = frappe.get_all("user_reg", fields=["name"])

    for user in all_users:
        user_doc = frappe.get_doc("user_reg", user.name)
        for file_entry in user_doc.codingfiles:
            if file_entry.name == file_uuid:
                file_entry.code = code
                user_doc.save()

                return {
                    "status": "success",
                    "message": {
                        "text": f"✅ File '{file_entry.filename}' updated successfully"
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
        "message": {
            "text": f"❌ File with UUID '{file_uuid}' not found"
        }
    }


import subprocess
@frappe.whitelist(allow_guest=True)
def execute(code, user_input=None):
    try:
        frappe.logger().info(f"Executing Code:\n{code}")
        
        # Split input by commas
        input_lines = user_input.split(",") if user_input else []
        input_data = "\n".join(input_lines) + "\n" if input_lines else ""
        
        # Run the Python script as a subprocess
        process = subprocess.Popen(
            ["python3", "-c", code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Pass input to the script
        output, error = process.communicate(input=input_data, timeout=5)
        
        # Process the output to remove input prompts that were already shown
        processed_output = output.strip()
        
        # Extract input prompts from code
        import re
        input_prompts = re.findall(r'input\([\'"](.+?)[\'"]\)', code)
        
        # Remove input prompts from output
        for prompt in input_prompts:
            processed_output = processed_output.replace(prompt, '', 1)
        
        # Clean up input artifacts
        processed_output = re.sub(r'\s*\n\s*\n', '\n', processed_output)
        
        frappe.logger().info(f"Processed Output:\n{processed_output}")
        frappe.logger().info(f"Error:\n{error}")
        
        return {
            "output": processed_output,
            "raw_output": output.strip(),  # Original output for debugging
            "error": error.strip()
        }
    except subprocess.TimeoutExpired:
        frappe.logger().error("Execution timed out.")
        return {"error": "Execution timed out."}
    except Exception as e:
        frappe.logger().error(f"Execution failed: {str(e)}")
        return {"error": str(e)}
    
import frappe
import subprocess

@frappe.whitelist(allow_guest=True)
def execute_c(code, user_input=None):
    try:
        frappe.logger().info("Executing C Code")

        # Handle multiline input from frontend
        if isinstance(user_input, list):
            input_data = "\n".join(user_input) + "\n"
        else:
            input_data = user_input.strip() + "\n" if user_input else ""

        # Save C code to a temp file
        with open("/tmp/program.c", "w") as f:
            f.write(code)

        # Compile the code
        compile_process = subprocess.run(
            ["gcc", "/tmp/program.c", "-o", "/tmp/program"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if compile_process.returncode != 0:
            return {
                "output": "",
                "error": compile_process.stderr.strip()
            }

        # Run the compiled program
        run_process = subprocess.Popen(
        ["stdbuf", "-oL", "/tmp/program"],  # -oL = line-buffered stdout
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        output, error = run_process.communicate(input=input_data, timeout=5)

        return {
            "output": output.strip(),
            "error": error.strip()
        }

    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out.", "output": ""}
    except Exception as e:
        return {"error": str(e), "output": ""}



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
    
    
"""Group"""

@frappe.whitelist(allow_guest=True)
def reg_group(groupname,description):
    global x
    if x is None:
        return {"message": "You should log in first.", "file": None}
    try:
        # Validate inputs
        if not groupname:
            return {"message": "All fields are required."}

        # Check if the group name already exists
        if frappe.db.exists("group", {"groupname": groupname, "groupowner": x}):
            return {"message": "Group name already exists."}

        # Create a new Group document
        group_doc = frappe.get_doc({
            "doctype": "group",
            "groupname": groupname,
            "groupowner": x,
            "description": description
        })
        group_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # Return success message
        return {"message": "Group registered successfully!", "name": group_doc.name}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Register Group Error")
        return {"message": f"An error occurred"}
 
   
@frappe.whitelist(allow_guest=True)  # Allow public access (optional)
def get_group_details(courseId):
    if not courseId:
        return {"error": _("Group ID is required")}
    
    # Fetch group details from the Groups Doctype - note the case sensitivity
    # Make sure "Group" matches your actual DocType name exactly
    group = frappe.get_value("group", courseId, ["groupname", "groupowner", "description"], as_dict=True)
    
    if not group:
        return {"error": _("Group not found")}
    
    return group  # ✅ Return group details directly

@frappe.whitelist(allow_guest=True)
def post_question(title, description, courseId):
    try:
        # Check if a question with the same title AND courseId already exists
        existing_question = frappe.db.exists("question", {"title": title, "courseid": courseId})

        if existing_question:
            return {"message": "Error: A question with this title already exists in this course."}

        # Create new document in "Question" Doctype
        question = frappe.get_doc({
            "doctype": "question",
            "title": title,
            "description": description,
            "courseid": courseId,
        })
        question.insert(ignore_permissions=True)  # Allow guest users to insert
        frappe.db.commit()  

        return {"message": "Question posted successfully!"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Post Question Error")
        return {"message": f"Error: {str(e)}"}

    
@frappe.whitelist(allow_guest=True)
def get_questions(courseId):
    try:
        # Fetch questions that match the provided course_id
        questions = frappe.get_all(
            "question",
            filters={"courseid": courseId},  # Compare course_id field
            fields=["name", "title", "description", "courseid"]
        )

        return {"questions": questions}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Questions Error")
        return {"message": f"Error: {str(e)}"}

    
@frappe.whitelist(allow_guest=True)
def join_project(course_id):
    global x  # Assuming x is the user ID

    try:
        # Check if the course_id exists in the "Group" Doctype (where name == course_id)
        if not frappe.db.exists("group", {"name": course_id}):
            return {"message": "Error: Group not found."}
        id=x
        
        # Fetch the Group document using course_id
        group = frappe.get_doc("group", course_id)

        # Ensure the child table 'group_members' exists
        if not hasattr(group, "group_members"):
            return {"message": "Error: Child table 'group_members' not found in Group document."}

        # Check if the user is already in the group_members child table
        for member in group.group_members:
            if member.users == id:  # 'users' field stores user IDs
                return {"message": "User already a member of the group."}

        # Append the user to the 'group_members' child table
        group.append("group_members", {"users": id})  # Assuming 'users' field holds user IDs

        # Save and commit changes
        group.save(ignore_permissions=True)
        frappe.db.commit()

        return {"message": "Course found."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Join Project Error")
        return {"message": f"Error: {str(e)}"}
    

"""Course.vue"""

@frappe.whitelist(allow_guest=True)
def get_courses():
    global x
    group_owner_id = "0194dc2e-157e-77d3-ac18-0063e13e3d8c"

    try:
        # Fetch records from the "Groups" DocType where groupowner matches the given ID
        groups = frappe.get_all("group", filters={"groupowner": x}, fields=["name", "groupname", "description", "groupowner"])
        
        return groups  # Returns a list of dictionaries containing all fields of the matched rows
    except Exception as e:
        frappe.log_error(f"Error fetching courses: {str(e)}", "get_courses")
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def courses_joined():
    global x  # Assuming x is the user ID
    id = "0194dc2e-157e-77d3-ac18-0063e13e3d8c"

    try:
        # Query to find parent records where 'id' exists in the child table 'group_members'
        groups = frappe.get_all(
            "group",
            filters=[["group_members", "users", "=", x]],  # Check in child table
            fields=["name", "groupname", "description", "groupowner"]  # Get parent fields
        )

        if not groups:
            return {"message": "No joined courses found."}

        return groups  # Returns list of matching groups

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Courses Joined Error")
        return {"message": f"Error: {str(e)}"}
    
@frappe.whitelist(allow_guest=True)
def get_members(course_id):
    try:
        group = frappe.get_doc("group", course_id)

        if not hasattr(group, "group_members") or not group.group_members:
            return {"message": None}

        # Extract only 'users' field from group_members
        user_ids = [member.users for member in group.group_members]

        if not user_ids:
            return {"message": None}

        # Query user_reg to get fullnames for matching user_ids
        user_fullnames = frappe.get_all(
            "user_reg",
            filters=[["name", "in", user_ids]],
            fields=["fullname"]
        )

        # Extract fullnames from the query result
        fullnames_list = [user["fullname"] for user in user_fullnames]

        return {"message": fullnames_list}  # Returns only the list of full names

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Members Error")
        return {"message": f"Error: {str(e)}"}
    
@frappe.whitelist(allow_guest=True)
def get_question_details(question_name, courseId):
    try:
        # Query to get the question document where title matches question_name and CourseId matches
        question = frappe.db.get_value("question", {"title": question_name, "courseid": courseId}, ["name", "title", "description"], as_dict=True)

        if not question:
            return {"message": "No matching question found for the given title and CourseId."}

        # Return the necessary fields
        return {
            "name": question.get("name"),
            "title": question.get("title"),
            "description": question.get("description")
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Question Details Error")
        return {"message": f"Error: {str(e)}"}


import frappe

@frappe.whitelist(allow_guest=True)
def createfile(questionTitle, courseId, filename, language):
    global x  # Using the global variable 'x' as the user

    try:
        if not (questionTitle and courseId and filename and language):
            return {"status": "error", "message": "Missing required parameters."}

        # Fetch the parent Question document
        question_name = frappe.get_value(
            "question",  # Ensure this is the correct parent Doctype name
            {"title": questionTitle, "courseid": courseId},
            "name"
        )

        if not question_name:
            return {"status": "error", "message": "No matching question found for the given title and courseId."}

        # Get the Question document
        question_doc = frappe.get_doc("question", question_name)

        # Check if the user already has an answer for this question
        existing_answer = next(
            (ans for ans in question_doc.answer if ans.user == x), None
        )

        if existing_answer:
            return {
                "status": "error",
                "message": "You have already created a file for this question.",
                "filename": existing_answer.filename
            }

        # Append new entry to the Answer child table
        new_answer = question_doc.append("answer", {
            "user": x,
            "filename": filename,
            "language": language
        })

        # Save the updated Question document
        question_doc.save(ignore_permissions=True)
        frappe.db.commit()

        # Return the generated name from the newly created entry
        return {
            "status": "success",
            "message": "Answer added successfully.",
            "data": {
                "name": new_answer.name,  # Auto-generated `name` field
                "user": x,
                "filename": filename,
                "language": language
            }
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Answer API Error")
        return {"status": "error", "message": f"Internal Server Error: {str(e)}"}


@frappe.whitelist(allow_guest=True)
def check_existing_file(questionTitle, courseId):
    global x
    try:
        # Check if the Question exists
        question_name = frappe.get_value(
            "question",
            {"title": questionTitle, "courseid": courseId},
            "name"
        )

        if not question_name:
            return {"status": "error", "message": "No matching question found."}

        # Check if an answer already exists for the user
        existing_file = frappe.db.get_value(
            "answer",
            {"parent": question_name, "user": x},
            ["filename", "name"],  # Fetch both filename and name
            as_dict=True  # Return as dictionary
        )

        if existing_file:
            return {
        "status": "exists",
        "filename": existing_file.get("filename"),  # Extract values correctly
        "name": existing_file.get("name")  # Include the generated name field
        }

        return {"status": "not_found"}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Check File API Error")
        return {"status": "error", "message": f"Internal Server Error: {str(e)}"}
    
@frappe.whitelist(allow_guest=True)
def getTitleDetails(questionTitle, courseId):
    try:
        # Fetch the Question document name (parent Doctype)
        question_name = frappe.get_value(
            "question",
            {"title": questionTitle, "courseid": courseId},
            "name"
        )
        if not question_name:
            return {"status": "error", "message": "No matching question found."}
        
        # Fetch details of the parent Question document
        question_doc = frappe.get_doc("question", question_name)
        
        # Extract required fields from Question (Parent)
        question_details = {
            "name": question_doc.name,
            "title": question_doc.title,
            "courseid": question_doc.courseid,
            "description": question_doc.description,
        }
        
        # Fetch all submitted answers (submitt = 1)
        submitted_answers = frappe.get_all(
            "answer",
            filters={"parent": question_name, "submitt": 1},
            fields=["name", "user", "corrected"]
        )
        
        # Fetch all unsubmitted answers (submitt = 0)
        unsubmitted_answers = frappe.get_all(
            "answer",
            filters={"parent": question_name, "submitt": "0" or 0},
            fields=["name", "user"]
        )
        
        # Extract user IDs from both submitted and unsubmitted answers
        user_ids = list(set([answer["user"] for answer in submitted_answers + unsubmitted_answers]))
        
        # Fetch full names of the users from `user_reg`
        user_fullnames = {}
        if user_ids:
            user_records = frappe.get_all(
                "user_reg",
                filters={"name": ["in", user_ids]},
                fields=["name", "fullname"]
            )
            user_fullnames = {user["name"]: user["fullname"] for user in user_records}
        
        # Format submitted answers with required fields
        formatted_submitted_answers = [
            {
                "filename": answer["name"],
                "fullname": user_fullnames.get(answer["user"], "Unknown User"),
                "corrected": int(answer.get("corrected", 0))
            }
            for answer in submitted_answers
        ]
        
        # Format unsubmitted answers with required fields
        formatted_unsubmitted_answers = [
            {
                "filename": answer["name"],
                "fullname": user_fullnames.get(answer["user"], "Unknown User")
            }
            for answer in unsubmitted_answers
        ]
        
        return {
            "status": "success",
            "question": question_details,
            "submitted_answers": formatted_submitted_answers,
            "unsubmitted_answers": formatted_unsubmitted_answers
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def updateCorrection(answer_id, corrected):
    try:
        # Ensure corrected is stored as an integer (1 or 0)
        corrected = int(corrected)

        # Update the 'corrected' field for the given answer
        frappe.db.set_value("answer", answer_id, "corrected", corrected)
        frappe.db.commit()

        return {"status": "success", "message": "Correction updated successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@frappe.whitelist(allow_guest=True)
def getFileName(search_fileid):
    if not search_fileid:
        return {"error": "Missing search_fileid parameter"}
    try:
        file_doc = frappe.db.get_value(
            "answer",
            {"name": search_fileid}, ["filename", "code", "submitt","corrected"])
        
        if file_doc:
            return {"filename": file_doc[0], "code": file_doc[1], "submitted": file_doc[2], "corrected": file_doc[3]}
        else:
            return {"error": "File not found"}
    except Exception as e:
        frappe.log_error(f"Error fetching file name: {str(e)}", "API Error")
        return {"error": "Internal Server Error"}
    
@frappe.whitelist(allow_guest=True)
def saveFileCode(file_id, code):
    if not file_id:
        return {"error": "Missing file_id parameter"}
    
    try:
        frappe.db.set_value("answer", file_id, "code", code)
        frappe.db.commit()
        return {"message": "Code updated successfully"}
    except Exception as e:
        frappe.log_error(f"Error saving code: {str(e)}", "API Error")
        return {"error": "Internal Server Error"}

@frappe.whitelist(allow_guest=True)
def toggleSubmit(file_id, submitt):
    if not file_id:
        return {"error": "Missing file_id parameter"}
    try:
        # Check if the file is already corrected
        corrected = frappe.db.get_value("answer", file_id, "corrected")
        
        # Convert to integers for comparison
        corrected = int(corrected) if corrected is not None else 0
        
        if corrected == 1:
            return {"error": "Already corrected"}
            
        # Only update if not corrected
        frappe.db.set_value("answer", file_id, "submitt", int(submitt))
        frappe.db.commit()
        return {"message": "Submission status updated", "submitt": int(submitt)}
    except Exception as e:
        frappe.log_error(f"Error updating submit status: {str(e)}", "API Error")
        return {"error": "Internal Server Error"}

@frappe.whitelist(allow_guest=True)
def get_coding_files():
    global x  # Assuming 'x' holds the current user's ID
    
    try:
        # Fetch the user document from 'user_reg' based on 'x'
        user = frappe.get_doc("user_reg", x)

        # Check if the user has the 'codingfiles' child table
        if not hasattr(user, "codingfiles"):
            return {"status": "error", "message": "Child table 'codingfiles' not found for the user."}

        # Extract the list of filenames and their corresponding name fields
        coding_files = [{"filename": file.filename, "name": file.name} for file in user.codingfiles]

        return {
            "status": "success",
            "message": "Files retrieved successfully.",
            "data": coding_files  # Return the list of coding files
        }

    except frappe.DoesNotExistError:
        return {"status": "error", "message": f"User with ID {x} does not exist."}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Coding Files Error")
        return {"status": "error", "message": f"An error occurred: {str(e)}"}
    
@frappe.whitelist(allow_guest=True)
def logout():
    global x  # Reference the global variable
    x = None  # Set global x to None
    frappe.cache().set_value("x", None)  # Store x as None in cache
    return {"status": "success", "message": "Logged out successfully", "Value": x}

@frappe.whitelist(allow_guest=True)
def deleteques(name):
    global x
    try:
        if not name or not x:
            return {"error": "Login required"}

        # Check if the question exists
        if not frappe.db.exists("question", name):
            return {"error": "Question not found"}

        # Delete the question
        frappe.delete_doc("Question", name, force=True)
        return {"message": "Question deleted successfully"}

    except Exception as e:
        return {"error": str(e)}

@frappe.whitelist(allow_guest=True)
def post_message(course_id, message_text):
    if not message_text.strip():
        return {"error": "Message cannot be empty."}

    new_message = frappe.get_doc({
        "doctype": "message",
        "courseid": course_id,
        "message_text": message_text,
        "sent_at": frappe.utils.now_datetime()  # Stores current timestamp
    })
    new_message.insert(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "message": "Message stored successfully"}


import frappe
from datetime import datetime, timedelta
import pytz  # Import for handling timezones

# Define Kolkata timezone
kolkata_tz = pytz.timezone("Asia/Kolkata")

@frappe.whitelist(allow_guest=True)
def get_messages(course_id):
    # Fetch current time in Kolkata timezone
    current_time = datetime.now(kolkata_tz)

    messages = frappe.get_all(
        "message",
        filters={"courseid": course_id},
        fields=["name", "message_text", "sent_at"],
        order_by="sent_at desc"
    )

    for msg in messages:
        msg["time_ago"] = format_time_ago(msg["sent_at"], current_time)

    return {"success": True, "messages": messages}  # ✅ Return without extra nesting

def format_time_ago(sent_at, current_time):
    # Convert sent_at if it's a string
    if isinstance(sent_at, str):
        sent_at = datetime.strptime(sent_at, "%Y-%m-%d %H:%M:%S.%f")
        sent_at = kolkata_tz.localize(sent_at)

    # Calculate time difference in seconds
    time_diff = (current_time - sent_at).total_seconds()

    # Format time ago string
    if time_diff < 60:
        return "Just now"
    elif time_diff < 3600:
        return f"{int(time_diff // 60)} minutes ago"
    elif sent_at.date() == current_time.date():
        return f"{int(time_diff // 3600)} hours ago"
    elif sent_at.date() == (current_time - timedelta(days=1)).date():
        return "Yesterday"
    elif time_diff < 7 * 86400:
        return f"{int(time_diff // 86400)} days ago"
    else:
        return sent_at.strftime("%b %d, %Y")
