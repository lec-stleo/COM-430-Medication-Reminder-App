import os
import tempfile
import unittest

from backend.app import create_app
from backend.app.config import Config


class TestConfig(Config):
    TESTING = True


class MedicationReminderAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")

        class LocalTestConfig(TestConfig):
            pass

        LocalTestConfig.DATABASE_PATH = self.db_path
        LocalTestConfig.INSTANCE_DIR = self.temp_dir.name
        LocalTestConfig.LOG_DIR = self.temp_dir.name
        LocalTestConfig.SECRET_KEY = "test-secret"

        self.app = create_app(LocalTestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def register_and_login(self):
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
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_end_to_end_medication_flow(self):
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
