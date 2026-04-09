"""Medication management API routes."""

from flask import Blueprint, current_app, jsonify, request, session

from ..services.medication_service import (
    create_medication,
    get_medication_for_user,
    list_medications_for_user,
)
from .auth_routes import login_required


medication_bp = Blueprint("medications", __name__)


@medication_bp.get("/medications")
@login_required
def list_medications():
    """Return all medications that belong to the active user."""
    medications = list_medications_for_user(session["user_id"])
    return jsonify({"medications": medications})


@medication_bp.post("/medications")
@login_required
def add_medication():
    """Create a new medication entry for the active user."""
    data = request.get_json(silent=True) or request.form
    name = (data.get("name") or "").strip()
    dosage = (data.get("dosage") or "").strip()
    med_status = (data.get("med_status") or "active").strip()
    photo_path = (data.get("photo_path") or "").strip() or None
    notes = (data.get("notes") or "").strip() or None

    if not name or not dosage:
        return jsonify({"error": "Medication name and dosage are required."}), 400

    medication_id = create_medication(
        session["user_id"],
        {
            "name": name,
            "dosage": dosage,
            "med_status": med_status,
            "photo_path": photo_path,
            "notes": notes,
        },
    )
    medication = get_medication_for_user(session["user_id"], medication_id)
    current_app.logger.info("Medication created for user %s: %s", session["user_id"], name)

    return jsonify(
        {
            "message": "Medication added successfully.",
            "medication": dict(medication),
        }
    ), 201
