"""Authentication API routes and session guards."""

from functools import wraps

from flask import Blueprint, current_app, jsonify, request, session

from ..services.auth_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_public_user_by_username,
    get_user_by_username,
    verify_user,
)


auth_bp = Blueprint("auth", __name__)


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


def login_required(view_function):
    """Ensure an API view is only accessible for an active authenticated session."""

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if not get_session_user():
            return jsonify({"error": "Authentication required."}), 401
        return view_function(*args, **kwargs)

    return wrapped_view


@auth_bp.post("/register")
def register():
    """Create a new user account and start a session."""
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    if get_user_by_username(username):
        return jsonify({"error": "Username already exists."}), 409
    if get_user_by_email(email):
        return jsonify({"error": "Email already exists."}), 409

    user_id = create_user(username, email, password)
    session["user_id"] = user_id
    current_app.logger.info("New user registered: %s", username)

    return jsonify(
        {
            "message": "Registration successful.",
            "user": {"id": user_id, "username": username, "email": email},
        }
    ), 201


@auth_bp.post("/login")
def login():
    """Authenticate an existing user and attach the user to the session."""
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = verify_user(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    session["user_id"] = user["id"]
    current_app.logger.info("User logged in: %s", username)
    return jsonify(
        {
            "message": "Login successful.",
            "user": {"id": user["id"], "username": user["username"]},
        }
    )


@auth_bp.post("/logout")
@login_required
def logout():
    """Remove the active user from the session."""
    user_id = session.pop("user_id", None)
    current_app.logger.info("User logged out: %s", user_id)
    return jsonify({"message": "Logout successful."})


@auth_bp.get("/me")
@login_required
def me():
    """Return the current authenticated user's profile."""
    user = get_session_user()
    return jsonify({"user": dict(user)})


@auth_bp.get("/<username>")
@login_required
def get_user(username):
    """Return the authenticated user's public profile by username."""
    current_user = get_session_user()
    if not current_user or current_user["username"] != username:
        return jsonify({"error": "You can only view your own profile."}), 403

    user = get_public_user_by_username(username)
    if not user:
        return jsonify({"error": "User not found."}), 404

    return jsonify({"user": dict(user)})
