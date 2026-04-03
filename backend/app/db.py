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
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create all database tables using the SQL schema file."""
    db = get_db()
    schema_path = Path(current_app.root_path) / "data" / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as schema_file:
        db.executescript(schema_file.read())
    db.commit()


def init_app(app):
    @app.before_request
    def ensure_database_exists():
        if not Path(app.config["DATABASE_PATH"]).exists():
            with app.app_context():
                init_db()
