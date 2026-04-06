# Medication Reminder System V1

Version 1 prototype for a DevOps-focused Medication Reminder System. This project uses Python, Flask, SQLite, and a simple HTML/CSS/JavaScript frontend.

## Why This Stack

- **Backend:** Flask
- **Frontend:** Server-rendered HTML templates with minimal JavaScript
- **Database:** SQLite

This combination is beginner-friendly, easy to run locally, and still clean enough to scale into a larger application later.

## Project Folder Structure

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

## Features Included

- User registration
- User login/logout
- Add medications
- Schedule medication reminders
- Mark medication as taken
- View medication adherence history
- Health route for environment checks
- Basic automated tests
- File and console logging

## Architecture Overview

### Layers

- **Frontend layer:** HTML templates, CSS, and minimal JavaScript
- **Route layer:** Flask Blueprints that expose pages and REST APIs
- **Service layer:** Business logic and database queries
- **Database layer:** SQLite with a SQL schema file

### Entities and Relationships

- **User**
  - One user can have many medications
  - One user can have many reminder logs
- **Medication**
  - Belongs to one user
  - Can have many schedules
- **Schedule**
  - Belongs to one medication
  - Can create many reminder logs over time
- **Reminder Log**
  - Belongs to one user
  - Belongs to one medication
  - Belongs to one schedule

## Database Schema

The database schema is stored in backend/app/data/schema.sql

### Tables

#### `users`

- `id`
- `username`
- `password_hash`
- `created_at`

#### `medications`

- `id`
- `user_id`
- `name`
- `dosage`
- `notes`
- `created_at`

#### `schedules`

- `id`
- `medication_id`
- `scheduled_date`
- `scheduled_time`
- `frequency`
- `status`
- `last_taken_at`
- `created_at`

#### `reminder_logs`

- `id`
- `schedule_id`
- `medication_id`
- `user_id`
- `action`
- `action_at`
- `notes`

## REST API Routes

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### Medications

- `GET /api/medications`
- `POST /api/medications`

### Schedules

- `GET /api/schedules`
- `POST /api/schedules`
- `PATCH /api/schedules/<schedule_id>/take`

### History

- `GET /api/history`

### System / DevOps

- `GET /api/health`
- `GET /api/test/ping`

## Environment Configuration

Copy `.env.example` to `.env` and adjust values if needed.

Example:

```env
SECRET_KEY=change-me-for-test-or-production
DATABASE_NAME=medication_reminder.db
INSTANCE_DIR=backend/instance
DATABASE_PATH=backend/instance/medication_reminder.db
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

Visit:

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
  "service": "medication-reminder-system",
  "status": "ok"
}
```

### 2. Confirm the test route works

Open:

- `GET /api/test/ping`

Expected result:

```json
{
  "message": "pong"
}
```

### 3. Create a test user

Go to:

- `/register`

Create a user such as:

- Username: `tester1`
- Password: `password123`

Expected result:

- You should be redirected to the dashboard
- A user session should be created

### 4. Add a medication

In the dashboard:

- Enter medication name
- Enter dosage
- Optionally enter notes
- Click **Save Medication**

Expected result:

- The medication appears in the medication list
- The medication becomes available in the schedule dropdown

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

### 6. Mark medication as taken

In the schedule list:

- Click **Mark as Taken**

Expected result:

- The schedule status changes to `taken`
- A reminder log entry is created

### 7. Validate adherence history

In the dashboard history section:

- Check that the medication appears in the history list

Expected result:

- The action should show `taken`
- The scheduled date/time should be visible
- The event timestamp should be recorded

### 8. Validate logs

Check the log file after running the app:

- `backend/logs/app.log`

Expected result:

- Login, registration, medication creation, and schedule updates should be logged

### 9. Run automated tests in Test

Execute:

```bash
python -m unittest discover -s tests -v
```

Expected result:

- Health route test passes
- End-to-end medication workflow test passes

## Notes About This V1

- This is intentionally simple and suitable for a prototype or class project
- Authentication uses Flask sessions
- Passwords are stored as hashed values, not plain text
- Frequency is stored as a simple label in Version 1
- SQLite is appropriate for local development and a lightweight Test environment
