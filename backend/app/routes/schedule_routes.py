from flask import Blueprint, current_app, jsonify, request, session

from ..services.medication_service import get_medication_for_user
from ..services.schedule_service import (
    create_schedule,
    list_schedules_for_user,
    update_schedule_action,
)
from .auth_routes import login_required


schedule_bp = Blueprint("schedules", __name__)


@schedule_bp.get("/schedules")
@login_required
def list_schedules():
    schedules = list_schedules_for_user(session["user_id"])
    return jsonify({"schedules": schedules})


@schedule_bp.post("/schedules")
@login_required
def add_schedule():
    data = request.get_json(silent=True) or request.form
    medication_id = data.get("medication_id")
    scheduled_date = (data.get("scheduled_date") or "").strip()
    scheduled_time = (data.get("scheduled_time") or "").strip()
    frequency = (data.get("frequency") or "").strip()
    start_date = (data.get("start_date") or "").strip() or scheduled_date
    end_date = (data.get("end_date") or "").strip() or None
    reminder_status = (data.get("reminder_status") or "enabled").strip()

    if not medication_id or not scheduled_date or not scheduled_time or not frequency:
        return jsonify({"error": "Medication, date, time, and frequency are required."}), 400

    medication = get_medication_for_user(session["user_id"], medication_id)
    if not medication:
        return jsonify({"error": "Medication not found."}), 404

    schedule_id = create_schedule(
        medication_id,
        scheduled_date,
        scheduled_time,
        frequency,
        start_date,
        end_date,
        reminder_status,
    )
    current_app.logger.info(
        "Schedule created for medication %s by user %s",
        medication_id,
        session["user_id"],
    )

    schedules = list_schedules_for_user(session["user_id"])
    schedule = next((item for item in schedules if item["id"] == schedule_id), None)

    return jsonify(
        {
            "message": "Schedule added successfully.",
            "schedule": schedule,
        }
    ), 201


@schedule_bp.patch("/schedules/<int:schedule_id>/take")
@login_required
def take_schedule(schedule_id):
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
    return jsonify(
        {
            "message": "Medication marked as taken.",
            "schedule": dict(updated_schedule),
        }
    )


@schedule_bp.patch("/schedules/<int:schedule_id>/skip")
@login_required
def skip_schedule(schedule_id):
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
    return jsonify(
        {
            "message": "Medication marked as skipped.",
            "schedule": dict(updated_schedule),
        }
    )
