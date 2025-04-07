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
    """Increment likes for LikeCounter named 'hey' and broadcast update."""
    doc_name = "hey"

    if not frappe.db.exists("LikeCounter", doc_name):
        return {"status": "error", "message": f"LikeCounter '{doc_name}' does not exist."}

    try:
        doc = frappe.get_doc("LikeCounter", doc_name)
        doc.likes += 1
        doc.save()
        frappe.db.commit()

        message = {
            "likes": doc.likes,
            "timestamp": frappe.utils.now(),
            "updated_by": frappe.session.user or "Guest"
        }

        # Broadcast to all tabs globally
        publish_realtime(
            event="update_likes",
            message=message,
            after_commit=True
        )

        return {
            "status": "success",
            **message,
            "broadcast_sent": True
        }
    except Exception as e:
        frappe.log_error(f"Error in send_like: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def get_likes():
    """Return current likes for LikeCounter named 'hey'."""
    doc_name = "hey"

    if not frappe.db.exists("LikeCounter", doc_name):
        return {"status": "error", "message": f"LikeCounter '{doc_name}' does not exist."}

    try:
        doc = frappe.get_doc("LikeCounter", doc_name)
        return {
            "likes": doc.likes,
            "timestamp": frappe.utils.now()
        }
    except Exception as e:
        frappe.log_error(f"Error in get_likes: {str(e)}")
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def check_realtime_status():
    """Check if realtime system (WebSocket) is working."""
    try:
        return {
            "status": "success",
            "realtime_enabled": bool(frappe.conf.get("enable_realtime", True)),
            "redis_status": "connected" if hasattr(frappe.cache(), "redis") else "not_connected",
            "timestamp": frappe.utils.now()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
