"""Unit tests for backend.utils.phone_prioritizer.prioritize.

These tests check that
1. The cleaned DataFrame contains **at most** five phone columns.
2. Preview metadata is sorted by priority in descending order.
3. Phone numbers with `CORRECT` status outrank others.
"""
from __future__ import annotations

from typing import List

import pandas as pd
import pytest

from backend.utils import phone_prioritizer as pp


def _build_sample_dataframe() -> pd.DataFrame:  # noqa: D401
    """Build a minimal DataFrame with six phone slots covering status variety."""
    data = {
        # Good number – should be ranked first
        "Phone 1": ["4053783205.0"],
        "Phone Status 1": ["CORRECT"],
        "Phone Type 1": ["MOBILE"],
        "Phone Tag 1": ["call_a02"],
        # Unknown but low call-count – expected runner-up
        "Phone 2": ["4053052196.0"],
        "Phone Status 2": ["UNKNOWN"],
        "Phone Type 2": ["MOBILE"],
        "Phone Tag 2": ["call_a00"],
        # Dead number should be ignored / low weight
        "Phone 3": ["4060005555.0"],
        "Phone Status 3": ["DEAD"],
        "Phone Type 3": ["LANDLINE"],
        "Phone Tag 3": ["call_a01"],
        # Wrong number
        "Phone 4": ["4052555529.0"],
        "Phone Status 4": ["WRONG"],
        "Phone Type 4": ["LANDLINE"],
        "Phone Tag 4": ["call_a05"],
        # No-answer with many call attempts
        "Phone 5": ["4059991234.0"],
        "Phone Status 5": ["NO_ANSWER"],
        "Phone Type 5": ["MOBILE"],
        "Phone Tag 5": ["call_a07"],
        # DNC – should have very negative score
        "Phone 6": ["4061111111.0"],
        "Phone Status 6": ["DNC"],
        "Phone Type 6": ["MOBILE"],
        "Phone Tag 6": ["call_a00"],
    }
    return pd.DataFrame(data)


def test_prioritize_returns_max_five_columns() -> None:
    """`prioritize` must limit output to five *Phone N* columns."""
    df = _build_sample_dataframe()
    cleaned, _ = pp.prioritize(df)

    phone_cols: List[str] = [c for c in cleaned.columns if c.startswith("Phone ")]
    assert len(phone_cols) <= 5, "More than five phone columns returned"


def test_meta_sorted_by_priority() -> None:
    """Preview metadata should be ordered from highest to lowest priority."""
    df = _build_sample_dataframe()
    _, meta = pp.prioritize(df)

    priorities = [m.priority for m in meta]
    assert priorities == sorted(priorities, reverse=True), "Meta not sorted by descending priority"


def test_correct_number_is_first_choice() -> None:
    """The phone with *CORRECT* status should have the highest priority score."""
    df = _build_sample_dataframe()
    _, meta = pp.prioritize(df)

    assert meta[0].status == "CORRECT", "First preview row is not a CORRECT number"