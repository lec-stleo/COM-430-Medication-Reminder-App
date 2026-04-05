from flask import Blueprint, jsonify


system_bp = Blueprint("system", __name__)


@system_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "medication-reminder-system"})


@system_bp.get("/test/ping")
def ping():
    return jsonify({"message": "pong"})
