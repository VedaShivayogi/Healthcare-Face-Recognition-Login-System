import hashlib
from functools import wraps

from flask import jsonify, redirect, request, session

from services.database import get_user_by_name, increment_failed_attempts, reset_failed_attempts, verify_pin, add_alert, log_access


def authenticate_user(username, pin):
    username = (username or "").strip()
    if not username or not pin:
        return {"success": False, "message": "Username and PIN are required."}

    user = get_user_by_name(username)
    if not user:
        return {"success": False, "message": "User not found."}

    if not bool(user.get("active", True)):
        add_alert("inactive_user", f"Inactive user attempted login: {username}", username)
        return {"success": False, "message": "This account is inactive."}

    if not verify_pin(username, pin):
        attempts = increment_failed_attempts(username)
        add_alert("failed_login", f"Failed PIN login for {username} after {attempts} failed attempts.", username)
        log_access(username, user.get("role", "Unknown"), "denied", method="pin")
        return {"success": False, "message": "Invalid PIN."}

    reset_failed_attempts(username)
    return {"success": True, "message": "PIN verified successfully.", "user": user}


def require_login(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect("/login")
        return view(*args, **kwargs)

    return wrapper


def require_roles(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not session.get("user"):
                return redirect("/login")
            role = session.get("role", "")
            if allowed_roles and role not in allowed_roles:
                return jsonify({"success": False, "message": "Access denied."}), 403
            return view(*args, **kwargs)

        return wrapper

    return decorator
