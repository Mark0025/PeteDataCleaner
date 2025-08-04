"""Integration test: run cleanup/prioritisation on real upload files.

The test scans the *upload/* directory for CSV files.  For every file that
is smaller than 2 MB (so CI remains fast) it runs:
    • trailing_dot_cleanup.clean_dataframe
    • phone_prioritizer.prioritize (only if at least one ``Phone`` column exists)

Assertions
----------
1. After cleanup no cell values end with the literal string ``.0``.
2. If phone columns exist, no more than five populated ``Phone N`` columns
   remain per record.
"""
from __future__ import annotations

import glob
from pathlib import Path
from typing import List

import pandas as pd
import pytest

from backend.utils import trailing_dot_cleanup as tdc
from backend.utils import phone_prioritizer as pp

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "upload"

@pytest.mark.parametrize("csv_path", [Path(p) for p in glob.glob(str(UPLOAD_DIR / "*.csv"))])
def test_upload_file_cleanup_and_phone_prio(csv_path: Path) -> None:  # noqa: D401
    if csv_path.stat().st_size > 2 * 1024 * 1024:
        pytest.skip("CSV too large for CI; functional path tested elsewhere")

    df = pd.read_csv(csv_path)
    cleaned = tdc.clean_dataframe(df)

    # --- 1. Assert no trailing .0 strings ---------------------------------
    str_values = cleaned.astype(str).stack()
    assert not str_values.str.endswith(".0").any(), "Trailing .0 values remain after cleanup"

    # --- 2. If phone columns exist, run prioritiser -----------------------
    phone_cols: List[str] = [c for c in cleaned.columns if c.startswith("Phone ") and c.count(" ") == 1]
    if phone_cols:
        cleaned2, _ = pp.prioritize(cleaned)
        populated = cleaned2[phone_cols].apply(lambda row: row.astype(str).str.strip().replace("", pd.NA).dropna(), axis=1)
        assert populated.apply(len).max() <= 5, "More than five phones populated after prioritization"