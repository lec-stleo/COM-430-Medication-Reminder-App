# Medication Reminder System

This repository contains the final submission of a Flask-based Medication Reminder System. The project was built in three stages to show clear improvement over time:

- `Version 1`: baseline medication reminder prototype
- `Version 2`: stronger CRUD, validation, notification simulation, and testing
- `Final`: recurring schedule behavior, safer rendering, stronger database constraints, shared auth/session helpers, and improved submission documentation

The application uses:

- Python
- Flask
- SQLite
- HTML, CSS, and JavaScript

Schedule date/time comparisons use the local timezone reported by the machine running the app.

Project history is tracked in [CHANGELOG.md](CHANGELOG.md).

## Final Submission Summary

The final project supports:

- user registration and login
- medication CRUD
- schedule CRUD
- recurring reminder behavior for daily and weekly schedules
- one-time and as-needed schedules
- marking medications as taken or skipped
- adherence history with occurrence-specific logging
- simulated email and push notifications
- upcoming schedule visibility
- health-check and logging support
- automated test coverage for core workflows and authorization boundaries

## Version Progression

### Version 1

Version 1 established the core application structure and baseline workflow:

- Flask application factory and startup path
- SQLite schema and data access helpers
- user registration and login
- medication creation
- schedule creation
- marking medications as taken
- reminder history
- server-rendered pages and basic dashboard JavaScript

### Version 2

Version 2 improved the prototype into a stronger test-ready application:

- medication edit and delete
- schedule edit and delete
- skip action for schedules
- upcoming schedule endpoint
- stronger route validation
- environment-based configuration
- file and console logging
- notification simulation
- notification log storage
- broader automated tests

### Final

The final submission closes the main gaps from the audit:

- recurring schedules now advance correctly for `daily` and `weekly` reminders
- `one-time` and `as-needed` schedules complete in place
- history and notification logs store the exact occurrence date/time
- dashboard editing uses inline forms instead of `prompt()`
- dashboard content is rendered safely through DOM APIs instead of raw HTML interpolation
- authentication/session helper logic is centralized
- database initialization is non-destructive by default
- schema `CHECK` constraints were expanded
- automated tests now include malformed input, protected-route access, and multi-user isolation
- workflow automation was updated to current GitHub Actions versions compatible with Node 24

## Business Requirements

The application is intended to satisfy these business needs:

1. A patient must be able to create an account and securely log in.
2. A patient must be able to create, view, update, and delete medication records.
3. A patient must be able to create, view, update, and delete reminder schedules.
4. A patient must be able to mark a scheduled medication as taken or skipped.
5. The system must preserve adherence history for each occurrence.
6. The system must support recurring schedules for common cases such as daily and weekly reminders.
7. The system must allow a user to view upcoming pending reminders.
8. The system must simulate reminder notifications for local/demo use without external services.
9. The system must keep data isolated per authenticated user.
10. The project must be simple to run locally and support automated verification.

## Functional Requirements by Version

### Version 1 Functions

- Register, log in, and log out
- Add medications
- Create schedules
- Mark schedules as taken
- View reminder history

### Version 2 Functions

- Edit/delete medications
- Edit/delete schedules
- Skip schedules
- Trigger notification simulation
- View notification logs
- View upcoming schedules through API

### Final Functions

- Recurring schedule advancement
- Inline dashboard edit forms
- Safer client-side rendering
- Shared session/auth guards
- Non-destructive DB initialization
- Expanded validation and authorization tests

## Architecture Overview

### Layers

- `Frontend layer`: Jinja templates, CSS, and dashboard JavaScript
- `Route layer`: Flask Blueprints for pages and REST-style endpoints
- `Service layer`: business logic and SQLite queries
- `Database layer`: SQLite schema and connection lifecycle helpers

### Folder Structure

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
│       │   ├── auth_helpers.py
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

## Module Mapping

### Application Core

- [backend/app/__init__.py](backend/app/__init__.py): app factory, logging, blueprint registration, CLI DB commands
- [backend/app/config.py](backend/app/config.py): environment-backed config values
- [backend/app/db.py](backend/app/db.py): SQLite connection handling and schema initialization
- [backend/app/models.py](backend/app/models.py): typed dictionary shapes for data records

### Route Modules

- [backend/app/routes/pages.py](backend/app/routes/pages.py): landing, login, register, dashboard pages
- [backend/app/routes/auth_helpers.py](backend/app/routes/auth_helpers.py): shared session/auth guard helpers
- [backend/app/routes/auth_routes.py](backend/app/routes/auth_routes.py): auth API routes
- [backend/app/routes/medication_routes.py](backend/app/routes/medication_routes.py): medication CRUD endpoints
- [backend/app/routes/schedule_routes.py](backend/app/routes/schedule_routes.py): schedule CRUD, take/skip, history
- [backend/app/routes/system_routes.py](backend/app/routes/system_routes.py): health and notification endpoints

### Service Modules

- [backend/app/services/auth_service.py](backend/app/services/auth_service.py): user lookup, password hashing, credential verification
- [backend/app/time_utils.py](backend/app/time_utils.py): system-clock time helpers for schedule comparisons
- [backend/app/services/medication_service.py](backend/app/services/medication_service.py): medication queries and persistence
- [backend/app/services/schedule_service.py](backend/app/services/schedule_service.py): schedule queries, recurring advancement, adherence actions
- [backend/app/services/history_service.py](backend/app/services/history_service.py): history and notification log queries
- [backend/app/services/notification_service.py](backend/app/services/notification_service.py): due-medication detection and notification simulation

### Frontend Modules

- [backend/app/templates/base.html](backend/app/templates/base.html): shared layout
- [backend/app/templates/index.html](backend/app/templates/index.html): landing page
- [backend/app/templates/login.html](backend/app/templates/login.html): login page
- [backend/app/templates/register.html](backend/app/templates/register.html): register page
- [backend/app/templates/dashboard.html](backend/app/templates/dashboard.html): dashboard structure
- [backend/app/static/js/app.js](backend/app/static/js/app.js): client-side dashboard behavior
- [backend/app/static/css/styles.css](backend/app/static/css/styles.css): styling

### Test Module

- [tests/test_app.py](tests/test_app.py): end-to-end route and workflow verification

## Data Model and Data Dictionary

The database schema is defined in [backend/app/data/schema.sql](backend/app/data/schema.sql).

### `users`

- `id`: primary key
- `username`: unique account name, required
- `email`: unique email address, required
- `password_hash`: hashed password, required
- `created_at`: timestamp of account creation

### `medications`

- `id`: primary key
- `user_id`: owner user ID
- `name`: medication name, required
- `dosage`: dosage string, required
- `med_status`: medication state, checked as `active`, `paused`, or `completed`
- `photo_path`: optional image/reference path
- `notes`: optional notes
- `created_at`: creation timestamp

### `schedules`

- `id`: primary key
- `medication_id`: related medication ID
- `scheduled_date`: next due occurrence date
- `scheduled_time`: due time
- `frequency`: checked as `daily`, `weekly`, `as-needed`, or `one-time`
- `start_date`: optional schedule start
- `end_date`: optional schedule end
- `reminder_status`: checked as `enabled` or `disabled`
- `status`: checked as `pending`, `taken`, or `skipped`
- `last_taken_at`: timestamp of most recent taken action
- `created_at`: creation timestamp

### `reminder_logs`

- `id`: primary key
- `schedule_id`: related schedule
- `medication_id`: related medication
- `user_id`: related user
- `action`: checked as `taken` or `skipped`
- `scheduled_date`: exact occurrence date that was acted on
- `scheduled_time`: exact occurrence time that was acted on
- `action_at`: timestamp of the logged action
- `notes`: optional notes

### `notification_logs`

- `id`: primary key
- `user_id`: related user
- `medication_id`: related medication
- `schedule_id`: related schedule
- `type`: checked as `email` or `push`
- `message`: notification message content
- `scheduled_date`: exact occurrence date the notification was tied to
- `scheduled_time`: exact occurrence time the notification was tied to
- `sent_at`: notification timestamp

## Application Behavior by Module

### Authentication

- Users register through `POST /api/auth/register`
- Passwords are hashed before storage
- Session-based authentication is used for protected routes
- Shared helper logic clears stale sessions automatically

### Medication Management

- Medications are scoped to the authenticated user
- The dashboard supports create, update, delete, and list flows
- Medication status can be active, paused, or completed

### Scheduling

- Daily and weekly schedules recur by advancing `scheduled_date`
- One-time and as-needed schedules remain single-occurrence
- Schedule validation checks IDs, dates, times, frequency, and date ranges
- Upcoming schedules and due-notification checks use the server's local system clock
- Upcoming schedules are limited to pending future occurrences

### Adherence History

- Every take/skip action writes a reminder log entry
- History records preserve the exact occurrence date/time acted on
- History is ordered newest first

### Notifications

- Notifications are simulated locally through a manual trigger endpoint
- Email and push notifications are written to the database and app logs
- Notification uniqueness is enforced per schedule, type, and occurrence

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

### System

- `GET /api/health`

## Notification Workflow

The project does not use background workers or third-party notification services. Instead, it uses a manual simulation flow for local development, testing, and demonstration.

1. A user creates a medication and schedule.
2. The schedule becomes due based on its stored occurrence date/time.
3. `POST /api/test/trigger-notifications` checks the authenticated user’s due schedules against the server's local clock.
4. The app simulates one email and one push notification.
5. Notification entries are stored in `notification_logs`.
6. Notification messages are also written to the application log.

## Environment Configuration

Copy `.env.example` to `.env` and adjust values if needed.

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

## Local Setup

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

## Database Initialization

- `flask init-db` creates missing tables and preserves existing data.
- `flask reset-db` is destructive and rebuilds the database from scratch.
- The schema includes indexes for common user, medication, and schedule lookup patterns.

## Testing and Evidence

### Automated Test Command

```bash
python -m unittest discover -s tests -v
```

### Current Automated Coverage Areas

- health endpoint
- guest vs authenticated page routing
- registration, login, logout, and profile access
- medication create, update, delete, and validation
- schedule create, update, delete, take, skip, and validation
- recurring schedule advancement
- one-time schedule completion behavior
- system-clock-based schedule comparisons
- upcoming schedules
- notification triggering and duplicate suppression
- protected-route authentication
- multi-user isolation
- non-destructive DB initialization

### Suggested Manual Evidence for Final Report

Add screenshots or screen recordings for:

- landing page
- registration flow
- dashboard with medication list
- schedule creation
- recurring schedule advancement after marking taken
- upcoming schedule list
- history log after take/skip actions
- notification log after manual trigger
- passing CI checks or terminal test output

## Known Limitations

- SQLite is used for local simplicity, not high-concurrency production use.
- Notification delivery is simulated rather than integrated with real email/push providers.
- Recurrence is intentionally limited to `daily` and `weekly` advancement; more complex rules are not implemented.
- The app uses session auth for a single web interface rather than full role-based access control.
- No background scheduler is used; reminders are triggered manually for demonstration/testing.
- Schedule timing depends on the local timezone configured on the machine running the app.

## Delivery Completeness

The final submission includes:

- source code for backend and frontend
- environment example file
- database schema
- automated tests
- GitHub Actions workflows
- changelog
- final report-style README with architecture, requirements, module mapping, data dictionary, and test guidance
