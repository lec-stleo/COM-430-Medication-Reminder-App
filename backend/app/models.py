from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    created_at: str


@dataclass
class Medication:
    id: int
    user_id: int
    name: str
    dosage: str
    med_status: str
    photo_path: Optional[str]
    notes: Optional[str]
    created_at: str


@dataclass
class Schedule:
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


@dataclass
class ReminderLog:
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
