"""
Trailing Dot Zero Cleanup Utility
--------------------------------
Utility functions to strip the common spreadsheet artefact of numbers
stored as floats ending in ``.0``.

It can operate on single values or entire pandas ``DataFrame`` objects
and is designed to be imported by backend/ frontend code as well as
invoked via the CLI.
"""

from __future__ import annotations

from typing import Any, List, Optional

import pandas as pd

__all__: list[str] = [
    "strip_trailing_dot_zero",
    "clean_dataframe",
]


def strip_trailing_dot_zero(value: Any) -> str:
    """Return *value* as a cleaned string with trailing ``.0`` removed.

    Examples
    --------
    >>> strip_trailing_dot_zero(4098880401.0)
    '4098880401'
    >>> strip_trailing_dot_zero("123.0")
    '123'
    >>> strip_trailing_dot_zero("ABC.0")
    'ABC.0'

    Parameters
    ----------
    value:
        Anything that represents a cell value. ``NaN`` and missing
        values are converted to an empty string.

    Returns
    -------
    str
        Cleaned representation.
    """

    if pd.isna(value):  # type: ignore[arg-type]
        return ""

    text = str(value)
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text


def clean_dataframe(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Return a *copy* of *df* with trailing ``.0`` removed.

    Parameters
    ----------
    df:
        Source dataframe.
    columns:
        Sub-set of column names to process.  If *None*, every object or
        numeric column is scanned.
    """

    cleaned = df.copy()

    target_cols: List[str]
    if columns is not None:
        target_cols = [c for c in columns if c in cleaned.columns]
    else:
        # Process object + numeric dtypes only to avoid datetime, bool …
        target_cols = [
            c
            for c in cleaned.columns
            if pd.api.types.is_object_dtype(cleaned[c])
            or pd.api.types.is_numeric_dtype(cleaned[c])
        ]

    for col in target_cols:
        cleaned[col] = cleaned[col].apply(strip_trailing_dot_zero)

    return cleaned
