"""Schedule, adherence, and history API routes."""

from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, session

from ..services.history_service import list_history_for_user
from ..services.medication_service import get_medication_for_user
from ..services.schedule_service import (
    create_schedule,
    delete_schedule,
    get_schedule_for_user,
    list_schedules_for_user,
    list_upcoming_schedules_for_user,
    update_schedule,
    update_schedule_action,
)
from .auth_routes import login_required


schedule_bp = Blueprint("schedules", __name__)


VALID_FREQUENCIES = {"daily", "weekly", "as-needed", "one-time"}


def _schedule_error(message):
    """Return a normalized schedule validation error response tuple."""
    return None, jsonify({"error": message}), 400


def _clean_schedule_payload(data):  # pylint: disable=too-many-return-statements
    medication_id = data.get("medication_id")
    scheduled_date = (data.get("scheduled_date") or "").strip()
    scheduled_time = (data.get("scheduled_time") or "").strip()
    frequency = (data.get("frequency") or "").strip().lower()
    start_date = (data.get("start_date") or "").strip() or scheduled_date
    end_date = (data.get("end_date") or "").strip() or None
    reminder_status = (data.get("reminder_status") or "enabled").strip()

    if not medication_id or not scheduled_date or not scheduled_time or not frequency:
        return _schedule_error("Medication, date, time, and frequency are required.")
    try:
        medication_id = int(medication_id)
    except (TypeError, ValueError):
        return _schedule_error("Medication ID must be a valid number.")

    try:
        # Parsing here keeps invalid date/time strings from failing later inside
        # recurring logic or notification checks.
        scheduled_date_value = datetime.strptime(scheduled_date, "%Y-%m-%d").date()
        start_date_value = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_value = (
            datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        )
        datetime.strptime(scheduled_time, "%H:%M")
    except ValueError:
        return _schedule_error(
            "Schedule date/time must use YYYY-MM-DD and HH:MM formats."
        )

    if frequency not in VALID_FREQUENCIES:
        return _schedule_error(
            "Frequency must be daily, weekly, as-needed, or one-time."
        )
    if reminder_status not in {"enabled", "disabled"}:
        return _schedule_error("Reminder status must be enabled or disabled.")
    if scheduled_date_value < start_date_value:
        return _schedule_error("Scheduled date cannot be earlier than the start date.")
    if end_date_value and end_date_value < start_date_value:
        return _schedule_error("End date cannot be earlier than the start date.")

    return {
        "medication_id": medication_id,
        "scheduled_date": scheduled_date,
        "scheduled_time": scheduled_time,
        "frequency": frequency,
        "start_date": start_date,
        "end_date": end_date,
        "reminder_status": reminder_status,
    }, None, None


@schedule_bp.get("/schedules")
@login_required
def list_schedules():
    """Return all schedules that belong to the active user."""
    schedules = list_schedules_for_user(session["user_id"])
    return jsonify({"schedules": schedules})


@schedule_bp.get("/schedules/upcoming")
@login_required
def upcoming_schedules():
    """Return upcoming pending schedules for the active user."""
    schedules = list_upcoming_schedules_for_user(session["user_id"])
    return jsonify({"schedules": schedules})


@schedule_bp.post("/schedules")
@login_required
def add_schedule():
    """Create a medication schedule for the active user."""
    data = request.get_json(silent=True) or request.form
    payload, error_response, status_code = _clean_schedule_payload(data)
    if error_response:
        return error_response, status_code

    medication = get_medication_for_user(session["user_id"], payload["medication_id"])
    if not medication:
        return jsonify({"error": "Medication not found."}), 404

    schedule_id = create_schedule(payload["medication_id"], payload)
    current_app.logger.info(
        "Schedule created for medication %s by user %s",
        payload["medication_id"],
        session["user_id"],
    )

    # Re-read from the list endpoint query so the response shape matches what the dashboard expects.
    schedules = list_schedules_for_user(session["user_id"])
    schedule = next((item for item in schedules if item["id"] == schedule_id), None)
    return jsonify({"message": "Schedule added successfully.", "schedule": schedule}), 201


@schedule_bp.put("/schedules/<int:schedule_id>")
@login_required
def edit_schedule(schedule_id):
    """Update one schedule owned by the active user."""
    existing_schedule = get_schedule_for_user(session["user_id"], schedule_id)
    if not existing_schedule:
        return jsonify({"error": "Schedule not found."}), 404

    data = request.get_json(silent=True) or request.form
    payload, error_response, status_code = _clean_schedule_payload(data)
    if error_response:
        return error_response, status_code

    medication = get_medication_for_user(session["user_id"], payload["medication_id"])
    if not medication:
        return jsonify({"error": "Medication not found."}), 404

    update_schedule(schedule_id, session["user_id"], payload)
    current_app.logger.info("Schedule updated for user %s: %s", session["user_id"], schedule_id)
    schedules = list_schedules_for_user(session["user_id"])
    schedule = next((item for item in schedules if item["id"] == schedule_id), None)
    return jsonify({"message": "Schedule updated successfully.", "schedule": schedule})


@schedule_bp.delete("/schedules/<int:schedule_id>")
@login_required
def remove_schedule(schedule_id):
    """Delete one schedule owned by the active user."""
    existing_schedule = get_schedule_for_user(session["user_id"], schedule_id)
    if not existing_schedule:
        return jsonify({"error": "Schedule not found."}), 404

    delete_schedule(schedule_id, session["user_id"])
    current_app.logger.info("Schedule deleted for user %s: %s", session["user_id"], schedule_id)
    return jsonify({"message": "Schedule deleted successfully."})


@schedule_bp.patch("/schedules/<int:schedule_id>/take")
@login_required
def take_schedule(schedule_id):
    """Mark a scheduled dose as taken and store an adherence log."""
    # Notes are optional and intentionally lightweight for a small class project.
    data = request.get_json(silent=True) or {}
    notes = (data.get("notes") or "").strip() or None

    updated_schedule = update_schedule_action(session["user_id"], schedule_id, "taken", notes)
    if not updated_schedule:
        return jsonify({"error": "Schedule not found."}), 404

    current_app.logger.info(
        "Schedule %s marked as taken by user %s",
        schedule_id,
        session["user_id"],
    )
    return jsonify({"message": "Medication marked as taken.", "schedule": dict(updated_schedule)})


@schedule_bp.patch("/schedules/<int:schedule_id>/skip")
@login_required
def skip_schedule(schedule_id):
    """Mark a scheduled dose as skipped and store an adherence log."""
    data = request.get_json(silent=True) or {}
    notes = (data.get("notes") or "").strip() or None

    updated_schedule = update_schedule_action(session["user_id"], schedule_id, "skipped", notes)
    if not updated_schedule:
        return jsonify({"error": "Schedule not found."}), 404

    current_app.logger.info(
        "Schedule %s marked as skipped by user %s",
        schedule_id,
        session["user_id"],
    )
    return jsonify({"message": "Medication marked as skipped.", "schedule": dict(updated_schedule)})


@schedule_bp.get("/history")
@login_required
def history():
    """Return medication adherence history for the active user."""
    history_items = list_history_for_user(session["user_id"])
    return jsonify({"history": history_items})
