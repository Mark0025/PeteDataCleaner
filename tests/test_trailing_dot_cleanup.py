"""Tests for trailing_dot_cleanup utility."""

from typing import List

import numpy as np
import pandas as pd
import pytest

from backend.utils import trailing_dot_cleanup as tdc


@pytest.mark.parametrize(
    "value, expected",
    [
        (4098880401.0, "4098880401"),
        ("8702853184.0", "8702853184"),
        ("4054104179", "4054104179"),
        (np.nan, ""),
        ("ABC.0", "ABC.0"),  # non-numeric string should remain
    ],
)
def test_strip_trailing_dot_zero(value: object, expected: str) -> None:
    """strip_trailing_dot_zero removes numeric .0 but leaves others."""
    assert tdc.strip_trailing_dot_zero(value) == expected


def test_clean_dataframe_selective() -> None:
    """clean_dataframe cleans specified columns only."""
    df = pd.DataFrame(
        {
            "Phone 1": [123.0, 456.0, "789.0"],
            "Zip": ["73034.0", "90210.0", "10001.0"],
            "Name": ["Alice", "Bob", "Charlie"],
        }
    )

    cleaned = tdc.clean_dataframe(df, columns=["Phone 1", "Zip"])

    assert cleaned["Phone 1"].tolist() == ["123", "456", "789"]
    assert cleaned["Zip"].tolist() == ["73034", "90210", "10001"]
    # Unspecified column remains unchanged
    assert cleaned["Name"].tolist() == ["Alice", "Bob", "Charlie"]


def test_clean_dataframe_auto_detect() -> None:
    """clean_dataframe auto-detects object/numeric columns when *columns* is None."""
    df = pd.DataFrame({"Col": [1.0, 2.0, 3.0], "Other": ["X", "Y", "Z"]})
    cleaned = tdc.clean_dataframe(df)
    assert cleaned["Col"].tolist() == ["1", "2", "3"]
