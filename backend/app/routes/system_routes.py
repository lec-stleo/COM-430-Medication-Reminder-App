"""System-level health and diagnostic routes."""

from flask import Blueprint, current_app, jsonify, session

from ..services.history_service import list_notifications_for_user
from ..services.notification_service import check_due_medications
from .auth_routes import login_required


system_bp = Blueprint("system", __name__)


@system_bp.get("/health")
def health():
    """Return a simple health payload for uptime checks."""
    return jsonify(
        {
            "status": "ok",
            "service": "medication-reminder-system",
            "environment": current_app.config["APP_ENV"],
        }
    )


@system_bp.post("/test/trigger-notifications")
@login_required
def trigger_notifications():
    """Run the local notification simulation for due medications."""
    notifications = check_due_medications(session["user_id"])
    return jsonify(
        {
            "message": "Notification check completed.",
            "triggered_count": len(notifications),
            "notifications": notifications,
        }
    )


@system_bp.get("/notifications")
@login_required
def notifications():
    """Return notification log entries for the active user."""
    return jsonify({"notifications": list_notifications_for_user(session["user_id"])})
