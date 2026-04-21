"""Helpers for interpreting schedule dates and times in the system timezone."""

from datetime import datetime


def system_timezone():
    """Return the local timezone reported by the host machine."""
    return datetime.now().astimezone().tzinfo


def current_schedule_time():
    """Return the current wall-clock time in the system timezone."""
    return datetime.now(system_timezone())


def parse_schedule_datetime(schedule_date, schedule_time):
    """Build a timezone-aware datetime for one stored schedule occurrence."""
    # Schedules are stored as separate date/time strings, so this helper gives
    # every due/upcoming comparison one consistent interpretation.
    naive_datetime = datetime.fromisoformat(f"{schedule_date}T{schedule_time}:00")
    return naive_datetime.replace(tzinfo=system_timezone())
