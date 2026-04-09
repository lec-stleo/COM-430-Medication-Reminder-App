"""Entity field definitions used to document the app's data model."""

from typing import Optional, TypedDict


class User(TypedDict):
    """Dictionary shape for user records."""

    id: int
    username: str
    email: str
    password_hash: str
    created_at: str


class Medication(TypedDict):
    """Dictionary shape for medication records."""

    id: int
    user_id: int
    name: str
    dosage: str
    med_status: str
    photo_path: Optional[str]
    notes: Optional[str]
    created_at: str


class Schedule(TypedDict):
    """Dictionary shape for schedule records."""

    id: int
    medication_id: int
    scheduled_date: str
    scheduled_time: str
    frequency: str
    start_date: Optional[str]
    end_date: Optional[str]
    reminder_status: str
    status: str
    last_taken_at: Optional[str]
    created_at: str


class ReminderLog(TypedDict):
    """Dictionary shape for reminder log records."""

    id: int
    schedule_id: int
    medication_id: int
    user_id: int
    action: str
    action_at: str
    notes: Optional[str]


ENTITY_RELATIONSHIPS = {
    "User": "One user can own many medications and many reminder logs.",
    "Medication": "One medication belongs to one user and can have many schedules.",
    "Schedule": "One schedule belongs to one medication and can produce many reminder logs.",
    "ReminderLog": "Each reminder log belongs to one user, one medication, and one schedule.",
}
