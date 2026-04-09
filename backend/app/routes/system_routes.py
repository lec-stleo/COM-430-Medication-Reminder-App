"""System-level health and diagnostic routes."""

from flask import Blueprint, jsonify


system_bp = Blueprint("system", __name__)


@system_bp.get("/health")
def health():
    """Return a simple health payload for uptime checks."""
    return jsonify({"status": "ok", "service": "medication-reminder-system"})


@system_bp.get("/test/ping")
def ping():
    """Return a lightweight test response for connectivity checks."""
    return jsonify({"message": "pong"})
