"""Helpers to compute distribution stats for phone status, type and tags."""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List
import pandas as pd

CALL_TAG_RE = re.compile(r"call_a(\d{2})", re.I)


def status_counts(df: pd.DataFrame) -> Dict[str, int]:
    counters: Counter = Counter()
    for col in df.filter(regex=r"^Phone Status ").columns:
        counters.update(df[col].astype(str).str.upper())
    counters.pop("nan", None)
    return dict(counters)


def type_counts(df: pd.DataFrame) -> Dict[str, int]:
    counters: Counter = Counter()
    for col in df.filter(regex=r"^Phone Type ").columns:
        counters.update(df[col].astype(str).str.upper())
    counters.pop("nan", None)
    return dict(counters)


def call_count_hist(df: pd.DataFrame) -> Dict[int, int]:
    counters: Counter[int] = Counter()
    for col in df.filter(regex=r"^Phone Tag ").columns:
        counters.update(
            df[col]
            .astype(str)
            .str.lower()
            .map(lambda v: int(CALL_TAG_RE.search(v).group(1)) if CALL_TAG_RE.search(v) else 0)
        )
    return dict(counters)
