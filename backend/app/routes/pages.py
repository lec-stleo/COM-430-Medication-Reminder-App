"""Server-rendered page routes for the browser-based UI."""

from flask import Blueprint, redirect, render_template, session, url_for

from ..services.auth_service import get_user_by_id

pages_bp = Blueprint("pages", __name__)


def has_active_session():
    """Return True when the browser session maps to a real user."""
    user_id = session.get("user_id")
    if not user_id:
        return False

    user = get_user_by_id(user_id)
    if not user:
        session.pop("user_id", None)
        return False

    return True


@pages_bp.get("/")
def home():
    """Render the landing page or redirect authenticated users to the dashboard."""
    if has_active_session():
        return redirect(url_for("pages.dashboard"))
    return render_template("index.html")


@pages_bp.get("/login")
def login_page():
    """Render the login page unless the user is already authenticated."""
    if has_active_session():
        return redirect(url_for("pages.dashboard"))
    return render_template("login.html")


@pages_bp.get("/register")
def register_page():
    """Render the registration page unless the user is already authenticated."""
    if has_active_session():
        return redirect(url_for("pages.dashboard"))
    return render_template("register.html")


@pages_bp.get("/dashboard")
def dashboard():
    """Render the dashboard for authenticated users only."""
    if not has_active_session():
        return redirect(url_for("pages.login_page"))
    return render_template("dashboard.html")
