"""Database connection helpers and schema initialization functions."""

import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    """Return one SQLite connection per request context."""
    if "db" not in g:
        database_path = current_app.config["DATABASE_PATH"]
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    """Close the active request database connection when one exists."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(reset=False):
    """Create database tables, optionally resetting the SQLite file first."""
    db = get_db()
    if reset:
        # Keep destructive behavior behind an explicit flag so normal startup
        # and `init-db` preserve existing demo/test data.
        db.executescript(
            """
            DROP TABLE IF EXISTS notification_logs;
            DROP TABLE IF EXISTS reminder_logs;
            DROP TABLE IF EXISTS schedules;
            DROP TABLE IF EXISTS medications;
            DROP TABLE IF EXISTS users;
            """
        )
    schema_path = Path(current_app.root_path) / "data" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as schema_file:
        db.executescript(schema_file.read())
    db.commit()


def init_app(app):
    """Attach database lifecycle hooks to the Flask application."""

    @app.before_request
    def ensure_database_exists():
        # The app lazily creates the SQLite file on first request so a fresh
        # clone can start without a separate manual bootstrap step.
        if not Path(app.config["DATABASE_PATH"]).exists():
            with app.app_context():
                init_db()


def fetch_all_dicts(query, params=()):
    """Run a SELECT query and return all rows as plain dictionaries."""
    db = get_db()
    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]
