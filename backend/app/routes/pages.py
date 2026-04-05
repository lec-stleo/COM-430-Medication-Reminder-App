from flask import Blueprint, redirect, render_template, session, url_for


pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("pages.dashboard"))
    return render_template("index.html")


@pages_bp.get("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("pages.dashboard"))
    return render_template("login.html")


@pages_bp.get("/register")
def register_page():
    if session.get("user_id"):
        return redirect(url_for("pages.dashboard"))
    return render_template("register.html")


@pages_bp.get("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("pages.login_page"))
    return render_template("dashboard.html")
