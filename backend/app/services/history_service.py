"""Reminder history data access helpers."""

from ..db import fetch_all_dicts


def list_history_for_user(user_id):
    """Return reminder log entries for a given user ordered by newest first."""
    return fetch_all_dicts(
        """
        SELECT
            rl.id,
            rl.action,
            rl.action_at,
            rl.notes,
            m.name AS medication_name,
            m.dosage,
            s.scheduled_date,
            s.scheduled_time,
            s.frequency
        FROM reminder_logs rl
        INNER JOIN medications m ON m.id = rl.medication_id
        INNER JOIN schedules s ON s.id = rl.schedule_id
        WHERE rl.user_id = ?
        ORDER BY rl.action_at DESC
        """,
        (user_id,),
    )
