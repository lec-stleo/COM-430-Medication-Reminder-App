from ..db import get_db


def list_schedules_for_user(user_id):
    db = get_db()
    rows = db.execute(
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
    ).fetchall()
    return [dict(row) for row in rows]


def create_schedule(
    medication_id,
    scheduled_date,
    scheduled_time,
    frequency,
    start_date,
    end_date,
    reminder_status,
):
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
            scheduled_date,
            scheduled_time,
            frequency,
            start_date,
            end_date,
            reminder_status,
        ),
    )
    db.commit()
    return cursor.lastrowid
