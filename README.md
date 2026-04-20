# Medication Reminder System

This project began as a **Version 1 prototype** for a DevOps-focused Medication Reminder System and has now been improved into a **Version 2 test-stage build**.

The application uses:

- Python
- Flask
- SQLite
- HTML, CSS, and minimal JavaScript

This stack stays beginner-friendly and easy to run locally while still being structured enough to demonstrate a realistic **Development -> Test** progression.

Project history is tracked in [CHANGELOG.md](CHANGELOG.md).

## Project Overview

The Medication Reminder System helps users:

- register and log in
- add medications
- create medication schedules
- mark medications as taken or skipped
- view medication adherence history
- simulate reminder notifications in Version 2

## Version Progression

### Version 1

Version 1 established the core workflow:

- user registration and login
- medication entry
- schedule creation
- marking medications as taken
- viewing reminder history

### Version 2

Version 2 keeps the same structure and improves it for test-stage readiness.

Main additions:

- edit and delete for medications
- edit and delete for schedules
- upcoming schedule view
- skip action for schedules
- stronger validation and cleaner error handling
- better environment configuration
- file and console logging
- simulated email and push notifications
- `notification_logs` storage
- manual notification trigger route
- broader automated test coverage

## Project Folder Structure

The structure remains close to Version 1, with only a small service addition for notifications.

```text
COM-430-Medication-Reminder-App/
├── backend/
│   ├── __init__.py
│   ├── run.py
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── db.py
│       ├── models.py
│       ├── data/
│       │   └── schema.sql
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── auth_routes.py
│       │   ├── medication_routes.py
│       │   ├── pages.py
│       │   ├── schedule_routes.py
│       │   └── system_routes.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   ├── history_service.py
│       │   ├── medication_service.py
│       │   ├── notification_service.py
│       │   └── schedule_service.py
│       ├── static/
│       │   ├── css/
│       │   │   └── styles.css
│       │   └── js/
│       │       └── app.js
│       └── templates/
│           ├── base.html
│           ├── dashboard.html
│           ├── index.html
│           ├── login.html
│           └── register.html
├── tests/
│   └── test_app.py
├── .env.example
├── requirements.txt
└── README.md
```

## Features

### Core Features from Version 1

- User registration
- User login/logout
- Add medications
- Create schedules
- Mark medications as taken
- View medication adherence history
- Health route for environment checks

### Added in Version 2

- Edit and delete medications
- Edit and delete schedules
- View upcoming schedules
- Mark medications as skipped
- Simulated email notifications
- Simulated push notifications
- Notification logs
- Manual notification trigger route
- Expanded automated tests
- More explicit validation and logging

## Architecture Overview

### Layers

- **Frontend layer:** HTML templates, CSS, and minimal JavaScript
- **Route layer:** Flask Blueprints that expose pages and REST APIs
- **Service layer:** business logic and database queries
- **Database layer:** SQLite with a SQL schema file

### Entities and Relationships

- **User**
  - One user can have many medications
  - One user can have many reminder logs
  - One user can have many notification logs
- **Medication**
  - Belongs to one user
  - Can have many schedules
  - Can appear in reminder and notification logs
- **Schedule**
  - Belongs to one medication
  - Stores the next due occurrence for recurring reminders
  - Can create many reminder logs over time
  - Can create notification log entries in Version 2
- **Reminder Log**
  - Belongs to one user
  - Belongs to one medication
  - Belongs to one schedule
- **Notification Log**
  - Belongs to one user
  - Belongs to one medication
  - Belongs to one schedule
  - Stores simulated email/push notification activity

## Database Schema

The database schema is stored in [backend/app/data/schema.sql](backend/app/data/schema.sql).

### Tables

#### `users`

- `id`
- `username`
- `email`
- `password_hash`
- `created_at`

#### `medications`

- `id`
- `user_id`
- `name`
- `dosage`
- `med_status`
- `photo_path`
- `notes`
- `created_at`

#### `schedules`

- `id`
- `medication_id`
- `scheduled_date`
- `scheduled_time`
- `frequency`
- `start_date`
- `end_date`
- `reminder_status`
- `status`
- `last_taken_at`
- `created_at`

#### `reminder_logs`

- `id`
- `schedule_id`
- `medication_id`
- `user_id`
- `action`
- `scheduled_date`
- `scheduled_time`
- `action_at`
- `notes`

#### `notification_logs`

- `id`
- `user_id`
- `medication_id`
- `schedule_id`
- `type`
- `message`
- `scheduled_date`
- `scheduled_time`
- `sent_at`

## REST API Routes

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/<username>`
- `GET /api/auth/me`

### Medications

- `GET /api/medications`
- `POST /api/medications`
- `PUT /api/medications/<id>`
- `DELETE /api/medications/<id>`

### Schedules

- `GET /api/schedules`
- `GET /api/schedules/upcoming`
- `POST /api/schedules`
- `PUT /api/schedules/<id>`
- `DELETE /api/schedules/<id>`
- `PATCH /api/schedules/<id>/take`
- `PATCH /api/schedules/<id>/skip`

### History and Notifications

- `GET /api/history`
- `GET /api/notifications`
- `POST /api/test/trigger-notifications`

### System / DevOps

- `GET /api/health`

## Notification System Process

Version 2 introduces a small notification foundation without adding background workers or external services.

### What Was Added

- A `notification_service.py` module
- A `check_due_medications()` function
- A `notification_logs` table
- A manual trigger endpoint for testing

### How It Works

1. A user creates a medication schedule.
2. When a schedule becomes due, Version 2 can simulate notifications.
3. The route `POST /api/test/trigger-notifications` runs the check manually.
4. The app simulates:
   - email notification
   - push notification
5. Each simulated notification is written to:
   - the console/log file
   - the `notification_logs` table

### Example Output

- `EMAIL SENT: Take Aspirin 100mg at 8:00 AM`
- `PUSH NOTIFICATION: Time to take your medication`

## Environment Configuration

Copy `.env.example` to `.env` and adjust values if needed.

Example:

```env
SECRET_KEY=change-me-for-test-or-production
APP_ENV=development
DEBUG=false
DATABASE_NAME=medication_reminder_v2.db
INSTANCE_DIR=backend/instance
DATABASE_PATH=backend/instance/medication_reminder_v2.db
LOG_DIR=backend/logs
TESTING=false
```

## How to Run Locally

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the environment file

```bash
cp .env.example .env
```

### 4. Start the Flask application

```bash
python backend/run.py
```

### 5. Open the app

```text
http://127.0.0.1:5000
```

## How to Run Tests

```bash
python -m unittest discover -s tests -v
```

## Step-by-Step Test Plan for a Test Environment

Use this flow after deploying or starting the application in a Test environment.

### 1. Confirm the service is running

Open:

- `GET /api/health`

Expected result:

```json
{
  "environment": "development",
  "service": "medication-reminder-system",
  "status": "ok"
}
```

### 2. Create a test user

Go to:

- `/register`

Create a user such as:

- Username: `tester1`
- Password: `password123`

Expected result:

- You should be redirected to the dashboard
- A user session should be created

### 3. Add a medication

In the dashboard:

- Enter medication name
- Enter dosage
- Optionally enter notes
- Click **Save Medication**

Expected result:

- The medication appears in the medication list
- The medication becomes available in the schedule dropdown

### 4. Edit the medication

In the medication list:

- Click **Edit**
- Update the name, dosage, or status

Expected result:

- The medication record updates in place

### 5. Create a schedule

In the dashboard:

- Select a medication
- Choose a date
- Choose a time
- Select a frequency
- Click **Create Schedule**

Expected result:

- The schedule appears in the schedule list
- Status should start as `pending`
- Daily and weekly schedules represent the next due occurrence for a recurring reminder
- One-time and as-needed schedules stay on a single occurrence until marked taken or skipped

### 6. Edit or delete the schedule

In the schedule list:

- Click **Edit** to update schedule details
- Click **Delete** to remove the schedule if needed

Expected result:

- The schedule list updates correctly

### 7. Mark medication as taken or skipped

In the schedule list:

- Click **Mark as Taken** or **Mark as Skipped**

Expected result:

- A reminder log entry is created for the exact occurrence date and time
- Daily and weekly schedules advance to their next due date until the end date is reached
- One-time and as-needed schedules change from `pending` to `taken` or `skipped`

### 8. Validate adherence history

In the dashboard history section:

- Check that the medication appears in the history list

Expected result:

- The action should show `taken` or `skipped`
- The scheduled date/time should be visible
- The event timestamp should be recorded

### 9. Trigger notifications

Use a schedule that is already due, then call:

- `POST /api/test/trigger-notifications`

Expected result:

- The response contains the triggered notifications
- Email and push simulation messages are generated
- Entries are stored in `notification_logs`

### 10. Validate logs

Check the log file after running the app:

- `backend/logs/app.log`

Expected result:

- Registration, login, medication changes, schedule changes, and notification simulation should be logged

### 11. Run automated tests in Test

Execute:

```bash
python -m unittest discover -s tests -v
```

Expected result:

- Health route test passes
- Registration/login test passes
- Medication update test passes
- Schedule/adherence test passes
- Notification trigger test passes

## How Version 2 Supports DevOps Promotion to Test Stage

Version 2 remains simple, but it is more test-ready than Version 1 because it now includes:

- environment-based configuration
- file and console logging
- stronger validation and clearer errors
- CRUD completeness for core features
- upcoming schedule visibility
- notification simulation that can be manually triggered
- notification logging for verification
- automated tests for the main workflows

## Notes

- Authentication uses Flask sessions
- Passwords are stored as hashed values, not plain text
- Daily and weekly schedules advance the stored `scheduled_date` to the next due occurrence
- One-time and as-needed schedules do not auto-advance
- SQLite is still appropriate for local development and a lightweight Test environment
- Version 2 intentionally keeps notification handling local and simple
