"""Schedule and adherence data access helpers."""

from datetime import datetime, timedelta

from ..db import fetch_all_dicts, get_db


def list_schedules_for_user(user_id):
    """Return all schedules owned by the given user."""
    return fetch_all_dicts(
        """
        SELECT
            s.id,
            s.medication_id,
            s.scheduled_date,
            s.scheduled_time,
            s.frequency,
            s.start_date,
            s.end_date,
            s.reminder_status,
            s.status,
            s.last_taken_at,
            s.created_at,
            m.name AS medication_name,
            m.dosage
        FROM schedules s
        INNER JOIN medications m ON m.id = s.medication_id
        WHERE m.user_id = ?
        ORDER BY s.scheduled_date ASC, s.scheduled_time ASC
        """,
        (user_id,),
    )


def list_upcoming_schedules_for_user(user_id):
    """Return pending schedules ordered by upcoming due time."""
    schedules = list_schedules_for_user(user_id)
    now = datetime.now()
    return [
        schedule
        for schedule in schedules
        if schedule["status"] == "pending"
        and datetime.fromisoformat(
            f'{schedule["scheduled_date"]}T{schedule["scheduled_time"]}:00'
        ) >= now
    ]


def create_schedule(medication_id, schedule_data):
    """Create a schedule record and return its identifier."""
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO schedules (
            medication_id,
            scheduled_date,
            scheduled_time,
            frequency,
            start_date,
            end_date,
            reminder_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            medication_id,
            schedule_data["scheduled_date"],
            schedule_data["scheduled_time"],
            schedule_data["frequency"],
            schedule_data["start_date"],
            schedule_data["end_date"],
            schedule_data["reminder_status"],
        ),
    )
    db.commit()
    return cursor.lastrowid


def update_schedule(schedule_id, user_id, schedule_data):
    """Update one schedule owned by the given user."""
    db = get_db()
    db.execute(
        """
        UPDATE schedules
        SET medication_id = ?,
            scheduled_date = ?,
            scheduled_time = ?,
            frequency = ?,
            start_date = ?,
            end_date = ?,
            reminder_status = ?
        WHERE id = ?
          AND medication_id IN (
              SELECT id FROM medications WHERE user_id = ?
          )
        """,
        (
            schedule_data["medication_id"],
            schedule_data["scheduled_date"],
            schedule_data["scheduled_time"],
            schedule_data["frequency"],
            schedule_data["start_date"],
            schedule_data["end_date"],
            schedule_data["reminder_status"],
            schedule_id,
            user_id,
        ),
    )
    db.commit()


def delete_schedule(schedule_id, user_id):
    """Delete one schedule owned by the given user."""
    db = get_db()
    db.execute(
        """
        DELETE FROM schedules
        WHERE id = ?
          AND medication_id IN (
              SELECT id FROM medications WHERE user_id = ?
          )
        """,
        (schedule_id, user_id),
    )
    db.commit()


def get_schedule_for_user(user_id, schedule_id):
    """Fetch one schedule record owned by the given user."""
    db = get_db()
    return db.execute(
        """
        SELECT
            s.*,
            m.user_id
        FROM schedules s
        INNER JOIN medications m ON m.id = s.medication_id
        WHERE s.id = ? AND m.user_id = ?
        """,
        (schedule_id, user_id),
    ).fetchone()


def update_schedule_action(user_id, schedule_id, action, notes=None):
    """Update a schedule status and record the adherence action in history."""
    db = get_db()
    schedule = get_schedule_for_user(user_id, schedule_id)
    if not schedule:
        return None

    current_scheduled_date = schedule["scheduled_date"]
    current_scheduled_time = schedule["scheduled_time"]
    next_scheduled_date = _next_scheduled_date(schedule)

    if next_scheduled_date:
        last_taken_at_value = "CURRENT_TIMESTAMP" if action == "taken" else "NULL"
        db.execute(
            f"""
            UPDATE schedules
            SET scheduled_date = ?,
                status = 'pending',
                last_taken_at = {last_taken_at_value}
            WHERE id = ?
            """,
            (next_scheduled_date, schedule_id),
        )
    elif action == "taken":
        db.execute(
            """
            UPDATE schedules
            SET status = 'taken',
                last_taken_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (schedule_id,),
        )
    else:
        db.execute(
            """
            UPDATE schedules
            SET status = 'skipped',
                last_taken_at = NULL
            WHERE id = ?
            """,
            (schedule_id,),
        )
    db.execute(
        """
        INSERT INTO reminder_logs (
            schedule_id,
            medication_id,
            user_id,
            action,
            scheduled_date,
            scheduled_time,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            schedule_id,
            schedule["medication_id"],
            user_id,
            action,
            current_scheduled_date,
            current_scheduled_time,
            notes,
        ),
    )
    db.commit()

    return db.execute(
        """
        SELECT
            s.id,
            s.medication_id,
            s.scheduled_date,
            s.scheduled_time,
            s.frequency,
            s.start_date,
            s.end_date,
            s.reminder_status,
            s.status,
            s.last_taken_at
        FROM schedules s
        WHERE s.id = ?
        """,
        (schedule_id,),
    ).fetchone()


def _next_scheduled_date(schedule):
    """Return the next due date for recurring schedules, or None when complete."""
    frequency = schedule["frequency"]
    if frequency not in {"daily", "weekly"}:
        return None

    current_date = datetime.strptime(schedule["scheduled_date"], "%Y-%m-%d").date()
    end_date = (
        datetime.strptime(schedule["end_date"], "%Y-%m-%d").date()
        if schedule["end_date"]
        else None
    )
    delta = timedelta(days=1 if frequency == "daily" else 7)
    next_date = current_date + delta

    if end_date and next_date > end_date:
        return None

    return next_date.isoformat()
