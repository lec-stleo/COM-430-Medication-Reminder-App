"""Automated tests for the medication reminder Flask application."""

from contextlib import ExitStack
from datetime import datetime, timedelta
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
                "APP_ENV": "test",
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

    def create_medication(self, name="Ibuprofen", dosage="200mg"):
        """Create a medication for the active test user."""
        return self.client.post(
            "/api/medications",
            json={
                "name": name,
                "dosage": dosage,
                "med_status": "active",
                "photo_path": "",
                "notes": "Take after meals",
            },
        )

    def test_health_route(self):
        """The health endpoint should return an OK status payload."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_registration_and_login(self):
        """A registered user should be able to log out and log back in."""
        register_response = self.client.post(
            "/api/auth/register",
            json={
                "username": "student1",
                "email": "student1@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(register_response.status_code, 201)
        self.client.post("/api/auth/logout")

        login_response = self.client.post(
            "/api/auth/login",
            json={"username": "student1", "password": "password123"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.get_json()["user"]["email"], "student1@example.com")

    def test_add_and_edit_medication(self):
        """A user can add a medication and update it later."""
        self.register_and_login()

        medication_response = self.create_medication()
        self.assertEqual(medication_response.status_code, 201)
        medication_id = medication_response.get_json()["medication"]["id"]

        update_response = self.client.put(
            f"/api/medications/{medication_id}",
            json={
                "name": "Ibuprofen",
                "dosage": "400mg",
                "med_status": "paused",
                "photo_path": "",
                "notes": "Updated dosage",
            },
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.get_json()["medication"]["dosage"], "400mg")

    def test_create_schedule_and_mark_taken(self):
        """A user can create a schedule and mark it as taken."""
        self.register_and_login()
        medication_id = self.create_medication().get_json()["medication"]["id"]

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

        take_response = self.client.patch(f"/api/schedules/{schedule_id}/take", json={})
        self.assertEqual(take_response.status_code, 200)
        self.assertEqual(take_response.get_json()["schedule"]["status"], "taken")

        history_response = self.client.get("/api/history")
        self.assertEqual(len(history_response.get_json()["history"]), 1)

    def test_trigger_notifications(self):
        """A due schedule should produce simulated notification log entries."""
        self.register_and_login()
        medication_id = self.create_medication(
            name="Aspirin",
            dosage="100mg",
        ).get_json()["medication"]["id"]
        due_time = datetime.utcnow() - timedelta(minutes=1)

        schedule_response = self.client.post(
            "/api/schedules",
            json={
                "medication_id": medication_id,
                "scheduled_date": due_time.strftime("%Y-%m-%d"),
                "scheduled_time": due_time.strftime("%H:%M"),
                "frequency": "daily",
                "start_date": due_time.strftime("%Y-%m-%d"),
                "end_date": "",
                "reminder_status": "enabled",
            },
        )
        self.assertEqual(schedule_response.status_code, 201)

        notification_response = self.client.post("/api/test/trigger-notifications")
        self.assertEqual(notification_response.status_code, 200)
        self.assertEqual(notification_response.get_json()["triggered_count"], 2)

        notifications_response = self.client.get("/api/notifications")
        notifications = notifications_response.get_json()["notifications"]
        self.assertEqual(len(notifications), 2)
        self.assertTrue(any(item["type"] == "email" for item in notifications))


if __name__ == "__main__":
    unittest.main()
