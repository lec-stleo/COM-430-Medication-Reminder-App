"""Simple notification simulation service for Version 2."""

from datetime import datetime

from flask import current_app

from ..db import fetch_all_dicts, get_db


def _is_due(schedule_row, now):
    scheduled_at = datetime.fromisoformat(
        f'{schedule_row["scheduled_date"]}T{schedule_row["scheduled_time"]}:00'
    )
    return schedule_row["status"] == "pending" and scheduled_at <= now


def check_due_medications(user_id):
    """Simulate sending email and push notifications for due medications."""
    now = datetime.utcnow()
    due_schedules = fetch_all_dicts(
        """
        SELECT
            s.id,
            s.medication_id,
            s.scheduled_date,
            s.scheduled_time,
            s.status,
            m.user_id,
            m.name,
            m.dosage
        FROM schedules s
        INNER JOIN medications m ON m.id = s.medication_id
        WHERE m.user_id = ?
          AND s.reminder_status = 'enabled'
        ORDER BY s.scheduled_date ASC, s.scheduled_time ASC
        """,
        (user_id,),
    )

    db = get_db()
    notifications = []

    for schedule in due_schedules:
        if not _is_due(schedule, now):
            continue

        time_label = datetime.strptime(
            schedule["scheduled_time"],
            "%H:%M",
        ).strftime("%I:%M %p").lstrip("0")
        email_message = (
            f'EMAIL SENT: Take {schedule["name"]} '
            f'{schedule["dosage"]} at {time_label}'
        )
        push_message = "PUSH NOTIFICATION: Time to take your medication"

        for notification_type, message in (
            ("email", email_message),
            ("push", push_message),
        ):
            existing = db.execute(
                """
                SELECT id
                FROM notification_logs
                WHERE schedule_id = ? AND type = ?
                """,
                (schedule["id"], notification_type),
            ).fetchone()
            if existing:
                continue

            cursor = db.execute(
                """
                INSERT INTO notification_logs (user_id, medication_id, schedule_id, type, message)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    schedule["medication_id"],
                    schedule["id"],
                    notification_type,
                    message,
                ),
            )
            current_app.logger.info(message)
            notifications.append(
                {
                    "id": cursor.lastrowid,
                    "user_id": user_id,
                    "medication_id": schedule["medication_id"],
                    "schedule_id": schedule["id"],
                    "type": notification_type,
                    "message": message,
                }
            )

    db.commit()
    return notifications
