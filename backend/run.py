"""Flask development entry point for the medication reminder app."""

from backend.app import create_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
