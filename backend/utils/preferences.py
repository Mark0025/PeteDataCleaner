"""Utility for persisting simple user preferences (JSON).
Currently supports maintaining a list of *always-hidden* DataFrame headers.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Set
from loguru import logger


PREF_DIR = Path(os.getenv("PETE_PREF_DIR", Path.home() / ".pete"))
PREF_DIR.mkdir(parents=True, exist_ok=True)
_HIDDEN_HEADERS_PATH = PREF_DIR / "hidden_headers.json"


def _read_json(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    try:
        with path.open("r", encoding="utf-8") as fh:
            return set(json.load(fh))
    except Exception as exc:  # pragma: no cover  (corrupt file)
        logger.error(f"Failed to read {path}: {exc}")
        return set()


def _write_json(path: Path, payload: Set[str]) -> None:
    try:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(sorted(payload), fh, indent=2)
    except Exception as exc:  # pragma: no cover
        logger.error(f"Failed to write {path}: {exc}")


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def load_hidden_headers() -> Set[str]:
    """Return the currently stored always-hidden headers."""
    return _read_json(_HIDDEN_HEADERS_PATH)


def add_hidden_headers(headers: List[str]) -> None:
    """Add *headers* to the persisted always-hidden list (idempotent)."""
    current = _read_json(_HIDDEN_HEADERS_PATH)
    updated = current.union(h.strip() for h in headers if h)
    _write_json(_HIDDEN_HEADERS_PATH, updated)
    logger.success(f"Persisted {len(headers)} new hidden headers ⇒ total {len(updated)}")
