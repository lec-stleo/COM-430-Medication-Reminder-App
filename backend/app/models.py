"""Typed record definitions used to document DB row shapes."""

from typing import Optional, TypedDict


class User(TypedDict):
    """Dictionary shape for user records."""

    # These TypedDicts act as lightweight documentation for SQLite row shapes.
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
    scheduled_date: str
    scheduled_time: str
    action_at: str
    notes: Optional[str]


class NotificationLog(TypedDict):
    """Dictionary shape for notification log records."""

    id: int
    user_id: int
    medication_id: int
    schedule_id: int
    type: str
    message: str
    scheduled_date: str
    scheduled_time: str
    sent_at: str
