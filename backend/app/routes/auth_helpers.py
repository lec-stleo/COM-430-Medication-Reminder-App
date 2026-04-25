"""Shared helpers for session-backed authentication checks."""

from functools import wraps
import secrets

from flask import jsonify, request, session

from ..services.auth_service import get_user_by_id

CSRF_SESSION_KEY = "csrf_token"


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


def get_csrf_token():
    """Return the active CSRF token, generating one when the session lacks it."""
    token = session.get(CSRF_SESSION_KEY)
    if not token:
        token = secrets.token_urlsafe(32)
        session[CSRF_SESSION_KEY] = token
    return token


def validate_csrf_request():
    """Return a JSON error response tuple when the CSRF token is missing or invalid."""
    expected_token = session.get(CSRF_SESSION_KEY)
    provided_token = request.headers.get("X-CSRF-Token")

    if not expected_token or not provided_token or provided_token != expected_token:
        return jsonify({"error": "Invalid or missing CSRF token."}), 400
    return None


def login_required(view_function):
    """Ensure an API view is only accessible for an active authenticated session."""

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        # Returning JSON here keeps API failures consistent across protected routes.
        if not get_session_user():
            return jsonify({"error": "Authentication required."}), 401
        return view_function(*args, **kwargs)

    return wrapped_view
