"""Test configuration shared across the suite.

Adds project root to ``sys.path`` so that ``import backend`` and
``import frontend`` work when the tests are executed via *uv run* (which
starts inside an isolated environment where ``pwd`` is no longer
automatically on *sys.path*).
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Silence all QMessageBox pop-ups during headless test runs.
# ---------------------------------------------------------------------------
from PyQt5 import QtWidgets  # noqa: E402  (import after sys.path tweak)
import pytest  # noqa: E402

@pytest.fixture(autouse=True)
def _patch_qmessagebox(monkeypatch):  # noqa: D401
    """Patch common QMessageBox methods so they don't block CI runs."""
    for method in ("information", "warning", "critical", "question"):
        monkeypatch.setattr(QtWidgets.QMessageBox, method, lambda *a, **k: None)
    yield