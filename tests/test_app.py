"""Automated tests for the medication reminder Flask application."""

from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
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

    def create_schedule(self, medication_id, **overrides):
        """Create a schedule for the active test user."""
        payload = {
            "medication_id": medication_id,
            "scheduled_date": "2026-04-10",
            "scheduled_time": "09:00",
            "frequency": "daily",
            "start_date": "2026-04-10",
            "end_date": "2026-04-20",
            "reminder_status": "enabled",
        }
        payload.update(overrides)

        return self.client.post(
            "/api/schedules",
            json=payload,
        )

    def test_health_route(self):
        """The health endpoint should return an OK status payload."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_page_routes_for_authenticated_and_guest_users(self):
        """Page routes should render or redirect based on session state."""
        home_response = self.client.get("/")
        self.assertEqual(home_response.status_code, 200)

        login_page_response = self.client.get("/login")
        self.assertEqual(login_page_response.status_code, 200)

        register_page_response = self.client.get("/register")
        self.assertEqual(register_page_response.status_code, 200)

        dashboard_redirect = self.client.get("/dashboard")
        self.assertEqual(dashboard_redirect.status_code, 302)
        self.assertIn("/login", dashboard_redirect.headers["Location"])

        self.register_and_login()

        home_redirect = self.client.get("/")
        self.assertEqual(home_redirect.status_code, 302)
        self.assertIn("/dashboard", home_redirect.headers["Location"])

        login_redirect = self.client.get("/login")
        self.assertEqual(login_redirect.status_code, 302)
        self.assertIn("/dashboard", login_redirect.headers["Location"])

        register_redirect = self.client.get("/register")
        self.assertEqual(register_redirect.status_code, 302)
        self.assertIn("/dashboard", register_redirect.headers["Location"])

        dashboard_response = self.client.get("/dashboard")
        self.assertEqual(dashboard_response.status_code, 200)

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

    def test_auth_validation_and_profile_access(self):
        """Auth routes should validate input and restrict profile access."""
        invalid_register_response = self.client.post(
            "/api/auth/register",
            json={
                "username": "ab",
                "email": "invalid-email",
                "password": "short",
            },
        )
        self.assertEqual(invalid_register_response.status_code, 400)

        me_unauthorized_response = self.client.get("/api/auth/me")
        self.assertEqual(me_unauthorized_response.status_code, 401)

        self.register_and_login()

        bad_login_response = self.client.post(
            "/api/auth/login",
            json={"username": "", "password": ""},
        )
        self.assertEqual(bad_login_response.status_code, 400)

        duplicate_username_response = self.client.post(
            "/api/auth/register",
            json={
                "username": "student1",
                "email": "student2@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(duplicate_username_response.status_code, 409)

        duplicate_email_response = self.client.post(
            "/api/auth/register",
            json={
                "username": "student2",
                "email": "student1@example.com",
                "password": "password123",
            },
        )
        self.assertEqual(duplicate_email_response.status_code, 409)

        me_response = self.client.get("/api/auth/me")
        self.assertEqual(me_response.status_code, 200)

        own_profile_response = self.client.get("/api/auth/student1")
        self.assertEqual(own_profile_response.status_code, 200)

        forbidden_profile_response = self.client.get("/api/auth/student2")
        self.assertEqual(forbidden_profile_response.status_code, 403)

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

    def test_medication_validation_and_delete(self):
        """Medication routes should validate input and support deletion."""
        self.register_and_login()

        invalid_medication_response = self.client.post(
            "/api/medications",
            json={
                "name": "",
                "dosage": "",
                "med_status": "unsupported",
                "photo_path": "",
                "notes": "",
            },
        )
        self.assertEqual(invalid_medication_response.status_code, 400)

        missing_medication_response = self.client.put(
            "/api/medications/999",
            json={
                "name": "Ibuprofen",
                "dosage": "200mg",
                "med_status": "active",
                "photo_path": "",
                "notes": "",
            },
        )
        self.assertEqual(missing_medication_response.status_code, 404)

        medication_id = self.create_medication().get_json()["medication"]["id"]

        list_response = self.client.get("/api/medications")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.get_json()["medications"]), 1)

        delete_response = self.client.delete(f"/api/medications/{medication_id}")
        self.assertEqual(delete_response.status_code, 200)

        delete_missing_response = self.client.delete(f"/api/medications/{medication_id}")
        self.assertEqual(delete_missing_response.status_code, 404)

    def test_create_schedule_and_mark_taken(self):
        """A user can create a schedule and mark it as taken."""
        self.register_and_login()
        medication_id = self.create_medication().get_json()["medication"]["id"]

        schedule_response = self.create_schedule(medication_id)
        self.assertEqual(schedule_response.status_code, 201)
        schedule_id = schedule_response.get_json()["schedule"]["id"]

        take_response = self.client.patch(f"/api/schedules/{schedule_id}/take", json={})
        self.assertEqual(take_response.status_code, 200)
        self.assertEqual(take_response.get_json()["schedule"]["status"], "taken")

        history_response = self.client.get("/api/history")
        self.assertEqual(len(history_response.get_json()["history"]), 1)

    def test_schedule_validation_update_delete_skip_and_upcoming(self):
        """Schedule routes should validate input and support V2 actions."""
        self.register_and_login()
        medication_id = self.create_medication().get_json()["medication"]["id"]

        invalid_schedule_response = self.client.post(
            "/api/schedules",
            json={
                "medication_id": "",
                "scheduled_date": "",
                "scheduled_time": "",
                "frequency": "",
                "start_date": "",
                "end_date": "",
                "reminder_status": "invalid",
            },
        )
        self.assertEqual(invalid_schedule_response.status_code, 400)

        future_schedule = self.create_schedule(
            medication_id,
            scheduled_date="2099-01-01",
            scheduled_time="08:30",
            start_date="2099-01-01",
            end_date="2099-01-02",
        )
        self.assertEqual(future_schedule.status_code, 201)
        schedule_id = future_schedule.get_json()["schedule"]["id"]

        upcoming_response = self.client.get("/api/schedules/upcoming")
        self.assertEqual(upcoming_response.status_code, 200)
        self.assertEqual(len(upcoming_response.get_json()["schedules"]), 1)

        update_response = self.client.put(
            f"/api/schedules/{schedule_id}",
            json={
                "medication_id": medication_id,
                "scheduled_date": "2099-01-02",
                "scheduled_time": "10:15",
                "frequency": "weekly",
                "start_date": "2099-01-02",
                "end_date": "2099-01-09",
                "reminder_status": "disabled",
            },
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.get_json()["schedule"]["frequency"], "weekly")

        missing_schedule_update = self.client.put(
            "/api/schedules/999",
            json={
                "medication_id": medication_id,
                "scheduled_date": "2099-01-02",
                "scheduled_time": "10:15",
                "frequency": "weekly",
                "start_date": "2099-01-02",
                "end_date": "2099-01-09",
                "reminder_status": "enabled",
            },
        )
        self.assertEqual(missing_schedule_update.status_code, 404)

        skipped_schedule = self.create_schedule(
            medication_id,
            scheduled_date="2026-04-11",
            scheduled_time="08:30",
            start_date="2026-04-11",
            end_date="",
        )
        skipped_schedule_id = skipped_schedule.get_json()["schedule"]["id"]

        skip_response = self.client.patch(
            f"/api/schedules/{skipped_schedule_id}/skip",
            json={},
        )
        self.assertEqual(skip_response.status_code, 200)
        self.assertEqual(skip_response.get_json()["schedule"]["status"], "skipped")

        delete_response = self.client.delete(f"/api/schedules/{schedule_id}")
        self.assertEqual(delete_response.status_code, 200)

        delete_missing_response = self.client.delete(f"/api/schedules/{schedule_id}")
        self.assertEqual(delete_missing_response.status_code, 404)

    def test_trigger_notifications(self):
        """A due schedule should produce simulated notification log entries."""
        self.register_and_login()
        medication_id = self.create_medication(
            name="Aspirin",
            dosage="100mg",
        ).get_json()["medication"]["id"]
        due_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)

        schedule_response = self.create_schedule(
            medication_id,
            scheduled_date=due_time.strftime("%Y-%m-%d"),
            scheduled_time=due_time.strftime("%H:%M"),
            start_date=due_time.strftime("%Y-%m-%d"),
            end_date="",
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
