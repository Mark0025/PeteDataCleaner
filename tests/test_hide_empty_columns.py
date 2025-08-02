"""Test hiding empty columns and persistence of hidden headers."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from backend.utils.data_type_converter import DataTypeConverter
from backend.utils import preferences as prefs


def test_filter_and_persist(tmp_path: Path, monkeypatch):
    # Monkeypatch preference dir to tmp
    monkeypatch.setenv("PETE_PREF_DIR", str(tmp_path))
    import importlib; importlib.reload(prefs)  # reload to use new env var

    df = pd.DataFrame({
        "A": [1, 2, 3],
        "B": [None, None, None],
        "C": [None, "", None],
    })

    cleaned = DataTypeConverter.filter_empty_columns(df, threshold=0.9)
    assert "B" not in cleaned.columns and "A" in cleaned.columns, "Empty column not removed or valuable column missing"

    prefs.add_hidden_headers(["B", "C"])
    stored_file = Path(tmp_path) / "hidden_headers.json"
    assert stored_file.exists(), "Preferences file not written"
    with stored_file.open() as fh:
        data = json.load(fh)
    assert set(data) == {"B", "C"}, "Hidden headers not persisted correctly"