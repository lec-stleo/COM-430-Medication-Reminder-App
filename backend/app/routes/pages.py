"""Server-rendered page routes for the browser-based UI."""

from flask import Blueprint, redirect, render_template, url_for

from .auth_helpers import has_active_session

pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def home():
    """Render the landing page or redirect authenticated users to the dashboard."""
    # The page routes are intentionally thin; most dynamic behavior happens
    # through the JSON API once the dashboard loads.
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
