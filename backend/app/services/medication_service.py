"""Medication data access helpers."""
# pylint: disable=duplicate-code

from ..db import fetch_all_dicts, get_db


def list_medications_for_user(user_id):
    """Return every medication that belongs to the given user."""
    # The schedule count is included here so the dashboard does not need
    # a second query per medication.
    return fetch_all_dicts(
        """
        SELECT
            m.id,
            m.user_id,
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
    )


def create_medication(user_id, medication_data):
    """Create a medication record for the given user and return its identifier."""
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO medications (user_id, name, dosage, med_status, photo_path, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            medication_data["name"],
            medication_data["dosage"],
            medication_data["med_status"],
            medication_data["photo_path"],
            medication_data["notes"],
        ),
    )
    db.commit()
    return cursor.lastrowid


def update_medication(medication_id, user_id, medication_data):
    """Update one medication owned by the given user."""
    db = get_db()
    db.execute(
        """
        UPDATE medications
        SET name = ?, dosage = ?, med_status = ?, photo_path = ?, notes = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            medication_data["name"],
            medication_data["dosage"],
            medication_data["med_status"],
            medication_data["photo_path"],
            medication_data["notes"],
            medication_id,
            user_id,
        ),
    )
    db.commit()


def delete_medication(medication_id, user_id):
    """Delete one medication owned by the given user."""
    db = get_db()
    db.execute(
        "DELETE FROM medications WHERE id = ? AND user_id = ?",
        (medication_id, user_id),
    )
    db.commit()


def get_medication_for_user(user_id, medication_id):
    """Fetch one medication record owned by the given user."""
    db = get_db()
    return db.execute(
        """
        SELECT *
        FROM medications
        WHERE id = ? AND user_id = ?
        """,
        (medication_id, user_id),
    ).fetchone()
