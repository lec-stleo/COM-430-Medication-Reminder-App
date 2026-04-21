"""Application factory and logging configuration for the Flask app."""

import logging
import os

from flask import Flask

from .config import Config
from .db import close_db, init_app as init_db_app, init_db
from .routes.auth_routes import auth_bp
from .routes.medication_routes import medication_bp
from .routes.pages import pages_bp
from .routes.schedule_routes import schedule_bp
from .routes.system_routes import system_bp


def create_app(config_class=Config):
    """Application factory used by the dev server and tests."""
    # The app factory keeps runtime configuration flexible for tests, local runs,
    # and any future deployment environments.
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(config_class)

    os.makedirs(app.config["INSTANCE_DIR"], exist_ok=True)
    os.makedirs(app.config["LOG_DIR"], exist_ok=True)

    configure_logging(app)
    init_db_app(app)

    app.teardown_appcontext(close_db)

    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(medication_bp, url_prefix="/api")
    app.register_blueprint(schedule_bp, url_prefix="/api")
    app.register_blueprint(system_bp, url_prefix="/api")

    @app.cli.command("init-db")
    def init_db_command():
        """Create any missing database tables without deleting existing data."""
        init_db()
        app.logger.info("Database initialized.")
        print("Database initialized.")

    @app.cli.command("reset-db")
    def reset_db_command():
        """Delete existing tables and rebuild the database schema from scratch."""
        # This is intentionally separate from init-db so destructive behavior is explicit.
        init_db(reset=True)
        app.logger.warning("Database reset and reinitialized.")
        print("Database reset and reinitialized.")

    return app


def configure_logging(app):
    """Write logs to both the console and a file for easier debugging."""
    # The project keeps logging simple: one file for review/debugging and one
    # stream handler for immediate terminal visibility.
    log_path = os.path.join(app.config["LOG_DIR"], "app.log")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    for handler in app.logger.handlers[:]:
        handler.close()
        app.logger.removeHandler(handler)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.propagate = False
