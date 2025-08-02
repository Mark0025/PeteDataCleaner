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
