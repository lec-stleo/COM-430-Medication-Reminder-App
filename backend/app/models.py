"""Entity field definitions used to document the app's data model."""

from typing import Optional, TypedDict


class User(TypedDict):
    id: int
    username: str
    email: str
    password_hash: str
    created_at: str


class Medication(TypedDict):
    id: int
    user_id: int
    name: str
    dosage: str
    med_status: str
    photo_path: Optional[str]
    notes: Optional[str]
    created_at: str


class Schedule(TypedDict):
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
    id: int
    schedule_id: int
    medication_id: int
    user_id: int
    action: str
    action_at: str
    notes: Optional[str]


class NotificationLog(TypedDict):
    id: int
    user_id: int
    medication_id: int
    schedule_id: int
    type: str
    message: str
    sent_at: str
