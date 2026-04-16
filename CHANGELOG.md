# Changelog

Notable changes to this project are documented in this file.

## [Final Projet]

- Placeholder section.

## [Version 2 Test Stage]

Version 2 keeps the Version 1 Flask and SQLite structure, then improves it for a Development -> Test promotion.

### Added

- Environment-based configuration updates for Version 2 test-stage setup
- Expanded database foundation and schema updates for Version 2
- Medication edit and delete support
- Schedule edit and delete support
- Upcoming schedule route
- Simulated notification workflow
- Notification trigger route
- Notification log route
- Notification service module
- Dashboard notification display and trigger action
- Expanded automated tests for Version 2 routes and workflows

### Changed

- README updated to document the Version 1 to Version 2 progression
- Authentication validation improved for registration and login
- Page route flow updated for Version 2 navigation behavior
- Dashboard UI updated to support medication and schedule edit/delete actions
- Test helpers refactored for pylint compliance

### Fixed

- Pylint issues across Version 2 modules and tests
- Test coverage gap for Version 2 routes and workflows
- Deprecation warning caused by `datetime.utcnow()` in notification-related test coverage

### Notes

- Version 2 keeps notifications local and simulated.
- The architecture remains close to Version 1 to stay easy to test.

## [Version 1 Prototype]

### Added

- Flask application configuration and startup flow
- SQLite schema, database helpers, and core models
- Authentication service and authentication API routes
- Page routes and server-rendered HTML templates
- Frontend styling and dashboard JavaScript behavior
- Medication management endpoints
- Schedule creation and listing endpoints
- Adherence action endpoints for marking schedules as taken or skipped
- Reminder history service and history route
- Backend automated test coverage

### Notes

- The application is focused on core medication reminder workflows.
