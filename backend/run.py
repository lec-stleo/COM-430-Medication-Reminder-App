"""Flask development entry point for the medication reminder app."""

from importlib import import_module
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

create_app = import_module("backend.app").create_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
