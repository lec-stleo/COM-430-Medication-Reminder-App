"""Medication management API routes."""

from flask import Blueprint, current_app, jsonify, request, session

from ..services.medication_service import (
    create_medication,
    delete_medication,
    get_medication_for_user,
    list_medications_for_user,
    update_medication,
)
from .auth_routes import login_required


medication_bp = Blueprint("medications", __name__)


def _clean_medication_payload(data):
    # Normalizing once here keeps the create and update endpoints aligned.
    name = (data.get("name") or "").strip()
    dosage = (data.get("dosage") or "").strip()
    med_status = (data.get("med_status") or "active").strip()
    photo_path = (data.get("photo_path") or "").strip() or None
    notes = (data.get("notes") or "").strip() or None

    if not name or not dosage:
        return (
            None,
            jsonify({"error": "Medication name and dosage are required."}),
            400,
        )
    if med_status not in {"active", "paused", "completed"}:
        return (
            None,
            jsonify(
                {
                    "error": (
                        "Medication status must be active, paused, or completed."
                    )
                }
            ),
            400,
        )

    return {
        "name": name,
        "dosage": dosage,
        "med_status": med_status,
        "photo_path": photo_path,
        "notes": notes,
    }, None, None


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
    payload, error_response, status_code = _clean_medication_payload(data)
    if error_response:
        return error_response, status_code

    medication_id = create_medication(session["user_id"], payload)
    medication = get_medication_for_user(session["user_id"], medication_id)
    current_app.logger.info(
        "Medication created for user %s: %s",
        session["user_id"],
        payload["name"],
    )

    return (
        jsonify(
            {
                "message": "Medication added successfully.",
                "medication": dict(medication),
            }
        ),
        201,
    )


@medication_bp.put("/medications/<int:medication_id>")
@login_required
def edit_medication(medication_id):
    """Update an existing medication owned by the active user."""
    # Ownership is checked before update so users cannot modify another user's data.
    medication = get_medication_for_user(session["user_id"], medication_id)
    if not medication:
        return jsonify({"error": "Medication not found."}), 404

    data = request.get_json(silent=True) or request.form
    payload, error_response, status_code = _clean_medication_payload(data)
    if error_response:
        return error_response, status_code

    update_medication(medication_id, session["user_id"], payload)
    current_app.logger.info(
        "Medication updated for user %s: %s",
        session["user_id"],
        medication_id,
    )
    updated = get_medication_for_user(session["user_id"], medication_id)
    return jsonify({"message": "Medication updated successfully.", "medication": dict(updated)})


@medication_bp.delete("/medications/<int:medication_id>")
@login_required
def remove_medication(medication_id):
    """Delete an existing medication owned by the active user."""
    medication = get_medication_for_user(session["user_id"], medication_id)
    if not medication:
        return jsonify({"error": "Medication not found."}), 404

    delete_medication(medication_id, session["user_id"])
    current_app.logger.info("Medication deleted for user %s: %s", session["user_id"], medication_id)
    return jsonify({"message": "Medication deleted successfully."})
