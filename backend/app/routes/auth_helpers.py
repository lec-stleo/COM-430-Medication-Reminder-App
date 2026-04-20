"""Shared helpers for session-backed authentication checks."""

from functools import wraps

from flask import jsonify, session

from ..services.auth_service import get_user_by_id


def get_session_user():
    """Return the currently logged-in user or clear a stale session."""
    user_id = session.get("user_id")
    if not user_id:
        return None

    user = get_user_by_id(user_id)
    if not user:
        session.pop("user_id", None)
        return None

    return user


def has_active_session():
    """Return True when the active session belongs to an existing user."""
    return get_session_user() is not None


def login_required(view_function):
    """Ensure an API view is only accessible for an active authenticated session."""

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if not get_session_user():
            return jsonify({"error": "Authentication required."}), 401
        return view_function(*args, **kwargs)

    return wrapped_view
