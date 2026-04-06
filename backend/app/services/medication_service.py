from ..db import get_db


def list_medications_for_user(user_id):
    db = get_db()
    rows = db.execute(
        """
        SELECT
            m.id,
            m.name,
            m.dosage,
            m.med_status,
            m.photo_path,
            m.notes,
            m.created_at,
            COUNT(s.id) AS schedule_count
        FROM medications m
        LEFT JOIN schedules s ON s.medication_id = m.id
        WHERE m.user_id = ?
        GROUP BY m.id
        ORDER BY m.created_at DESC
        """,
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def create_medication(user_id, name, dosage, med_status, photo_path, notes):
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO medications (user_id, name, dosage, med_status, photo_path, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, dosage, med_status, photo_path, notes),
    )
    db.commit()
    return cursor.lastrowid


def get_medication_for_user(user_id, medication_id):
    db = get_db()
    return db.execute(
        """
        SELECT *
        FROM medications
        WHERE id = ? AND user_id = ?
        """,
        (medication_id, user_id),
    ).fetchone()
