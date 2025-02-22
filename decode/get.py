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


import frappe
from frappe import publish_realtime

@frappe.whitelist()
def notify_typing(room_id, is_typing):
    """Broadcast typing status to room members"""
    user = "static_user@example.com"
    print(f"Backend received: room_id={room_id}, is_typing={is_typing}")  # Debug log
    
    try:
        publish_realtime(
            event='typing_update',
            message={
                'user': user,
                'is_typing': is_typing,
                'room_id': room_id
            },
            room=room_id
        )
        print(f"Successfully published realtime event for user {user}")  # Debug log
        return {"status": "success"}
    except Exception as e:
        print(f"Error publishing realtime event: {str(e)}")  # Debug log
        return {"status": "error", "message": str(e)}

import frappe
from frappe import publish_realtime

@frappe.whitelist()
def send_like():
    """Increment likes only for the existing LikeCounter document with name 'hey'."""
    doc_name = "hey"  # Target the specific existing document

    # Ensure the document exists
    if not frappe.db.exists("LikeCounter", doc_name):
        return {"status": "error", "message": f"LikeCounter '{doc_name}' does not exist."}

    # Fetch and update the existing document
    doc = frappe.get_doc("LikeCounter", doc_name)
    doc.likes += 1
    doc.save()
    frappe.db.commit()

    # Broadcast update
    publish_realtime(
        event="update_likes",
        message={"likes": doc.likes},
        user="all"
    )

    return {"status": "success", "likes": doc.likes}

import frappe

@frappe.whitelist(allow_guest=True)
def get_likes():
    doc_name = "hey"  # Target the specific existing document

    # Ensure the document exists
    if not frappe.db.exists("LikeCounter", doc_name):
        return {"status": "error", "message": f"LikeCounter '{doc_name}' does not exist."}

    # Fetch the document
    doc = frappe.get_doc("LikeCounter", doc_name)

    # Return the likes count
    return {"likes": doc.likes}  # Assuming 'likes' is a field in the LikeCounter Doctype

