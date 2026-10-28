import importlib
from pathlib import Path
import sys

import pytest


# Keep both `pytest -q` and `python -m pytest -q` usable without packaging the
# standalone programs or changing their imports.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def q1_checker(monkeypatch):
    # This checker consumes argv at import time, even when imported by pytest.
    monkeypatch.setattr(sys, "argv", ["q1_check.py"])
    return importlib.import_module("q1_check")
