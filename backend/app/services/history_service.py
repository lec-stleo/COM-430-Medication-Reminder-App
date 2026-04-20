"""Reminder history and notification log helpers."""

from ..db import fetch_all_dicts


def list_history_for_user(user_id):
    """Return reminder log entries for a given user ordered by newest first."""
    return fetch_all_dicts(
        """
        SELECT
            rl.id,
            rl.action,
            rl.scheduled_date,
            rl.scheduled_time,
            rl.action_at,
            rl.notes,
            m.name AS medication_name,
            m.dosage,
            s.frequency
        FROM reminder_logs rl
        INNER JOIN medications m ON m.id = rl.medication_id
        INNER JOIN schedules s ON s.id = rl.schedule_id
        WHERE rl.user_id = ?
        ORDER BY rl.action_at DESC
        """,
        (user_id,),
    )


def list_notifications_for_user(user_id):
    """Return notification log entries for a given user ordered by newest first."""
    return fetch_all_dicts(
        """
        SELECT
            nl.id,
            nl.user_id,
            nl.medication_id,
            nl.schedule_id,
            nl.type,
            nl.message,
            nl.scheduled_date,
            nl.scheduled_time,
            nl.sent_at,
            m.name AS medication_name,
            m.dosage
        FROM notification_logs nl
        INNER JOIN medications m ON m.id = nl.medication_id
        WHERE nl.user_id = ?
        ORDER BY nl.sent_at DESC
        """,
        (user_id,),
    )
