"""Automated tests for the medication reminder Flask application."""

from contextlib import ExitStack
import os
import tempfile
import unittest

from backend.app import create_app
from backend.app.config import Config


class MedicationReminderAppTests(unittest.TestCase):
    """End-to-end and route-level tests for the application."""

    def setUp(self):
        """Create an isolated app instance backed by a temporary SQLite file."""
        self.resource_stack = ExitStack()
        self.addCleanup(self.resource_stack.close)
        self.temp_dir = self.resource_stack.enter_context(tempfile.TemporaryDirectory())
        self.db_path = os.path.join(self.temp_dir, "test.db")

        local_test_config = type(
            "LocalTestConfig",
            (Config,),
            {
                "TESTING": True,
                "DATABASE_PATH": self.db_path,
                "INSTANCE_DIR": self.temp_dir,
                "LOG_DIR": self.temp_dir,
                "SECRET_KEY": "test-secret",
            },
        )

        self.app = create_app(local_test_config)
        self.client = self.app.test_client()

    def register_and_login(self):
        """Register the default test user and keep the resulting session."""
        response = self.client.post(
            "/api/auth/register",
            json={
                "username": "student1",
                "email": "student1@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(response.status_code, 201)

    def test_health_route(self):
        """The health endpoint should return an OK status payload."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_end_to_end_medication_flow(self):
        """A user can register, add a medication, schedule it, and mark it taken."""
        self.register_and_login()

        user_response = self.client.get("/api/auth/student1")
        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(user_response.get_json()["user"]["email"], "student1@example.com")

        medication_response = self.client.post(
            "/api/medications",
            json={
                "name": "Ibuprofen",
                "dosage": "200mg",
                "med_status": "active",
                "photo_path": "images/ibuprofen.jpg",
                "notes": "Take after meals",
            },
        )
        self.assertEqual(medication_response.status_code, 201)
        medication_id = medication_response.get_json()["medication"]["id"]
        self.assertEqual(medication_response.get_json()["medication"]["med_status"], "active")

        schedule_response = self.client.post(
            "/api/schedules",
            json={
                "medication_id": medication_id,
                "scheduled_date": "2026-04-10",
                "scheduled_time": "09:00",
                "frequency": "daily",
                "start_date": "2026-04-10",
                "end_date": "2026-04-20",
                "reminder_status": "enabled",
            },
        )
        self.assertEqual(schedule_response.status_code, 201)
        schedule_id = schedule_response.get_json()["schedule"]["id"]
        self.assertEqual(schedule_response.get_json()["schedule"]["reminder_status"], "enabled")

        take_response = self.client.patch(f"/api/schedules/{schedule_id}/take", json={})
        self.assertEqual(take_response.status_code, 200)
        self.assertEqual(take_response.get_json()["schedule"]["status"], "taken")

        history_response = self.client.get("/api/history")
        self.assertEqual(history_response.status_code, 200)
        history = history_response.get_json()["history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["medication_name"], "Ibuprofen")

    def test_skip_schedule_creates_history_entry(self):
        """Skipping a schedule should update its status and create a history row."""
        self.register_and_login()

        medication_response = self.client.post(
            "/api/medications",
            json={
                "name": "Vitamin D",
                "dosage": "500 IU",
                "med_status": "active",
                "photo_path": "",
                "notes": "Morning dose",
            },
        )
        medication_id = medication_response.get_json()["medication"]["id"]

        schedule_response = self.client.post(
            "/api/schedules",
            json={
                "medication_id": medication_id,
                "scheduled_date": "2026-04-11",
                "scheduled_time": "08:30",
                "frequency": "daily",
                "start_date": "2026-04-11",
                "end_date": "",
                "reminder_status": "enabled",
            },
        )
        schedule_id = schedule_response.get_json()["schedule"]["id"]

        skip_response = self.client.patch(f"/api/schedules/{schedule_id}/skip", json={})
        self.assertEqual(skip_response.status_code, 200)
        self.assertEqual(skip_response.get_json()["schedule"]["status"], "skipped")
        self.assertIsNone(skip_response.get_json()["schedule"]["last_taken_at"])

        history_response = self.client.get("/api/history")
        history = history_response.get_json()["history"]
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action"], "skipped")


if __name__ == "__main__":
    unittest.main()
