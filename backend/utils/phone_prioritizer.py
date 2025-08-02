"""Phone prioritization utility

Reduce up to 30 REISift phone columns to Pete's 5 phone slots based on
status, type and call-count tags.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import re
import pandas as pd

# Priority weights
STATUS_WEIGHT = {
    "CORRECT": 100,
    "UNKNOWN": 70,
    "NO_ANSWER": 50,
    "WRONG": 0,
    "DEAD": 0,
    "DNC": -100,
}

TYPE_BONUS = {
    "MOBILE": 10,
    "LANDLINE": 0,
    "UNKNOWN": 0,
}

CALL_COUNT_PENALTY = 5  # subtract (call_count * penalty)

CALL_TAG_RE = re.compile(r"call_a(\d{2})", re.I)

@dataclass
class PhoneMeta:
    column: str
    number: str
    status: str
    phone_type: str
    call_count: int
    priority: int


def _extract_call_count(tag_value: str) -> int:
    if not tag_value:
        return 0
    m = CALL_TAG_RE.search(str(tag_value))
    if m:
        return int(m.group(1))
    return 0


def prioritize(df: pd.DataFrame, max_phones: int = 5) -> Tuple[pd.DataFrame, List[PhoneMeta]]:
    """Return *(clean_df, meta_list)* with at most *max_phones* phone cols.

    Assumes REISift naming convention: Phone 1, Phone Status 1, Phone Type 1, Phone Tag 1 … up to 30.
    """
    phone_entries: List[PhoneMeta] = []
    for i in range(1, 31):
        col = f"Phone {i}"
        if col not in df.columns:
            continue
        status_val = str(df.get(f"Phone Status {i}", ""))
        type_val = str(df.get(f"Phone Type {i}", ""))
        tag_val = str(df.get(f"Phone Tag {i}", ""))
        call_count = _extract_call_count(tag_val)

        status_key = status_val.upper() if status_val else "UNKNOWN"
        type_key = type_val.upper() if type_val else "UNKNOWN"

        base = STATUS_WEIGHT.get(status_key, 0)
        bonus = TYPE_BONUS.get(type_key, 0)
        score = base + bonus - (call_count * CALL_COUNT_PENALTY) - i  # earlier cols slightly preferred

        phone_entries.append(
            PhoneMeta(
                column=col,
                number="",  # placeholder, not used here
                status=status_key,
                phone_type=type_key,
                call_count=call_count,
                priority=score,
            )
        )

    # Sort by priority DESC
    phone_entries.sort(key=lambda p: p.priority, reverse=True)
    selected = phone_entries[:max_phones]

    # Build new dataframe
    cleaned_df = df.copy()

    # Drop all phone/type/status/tag columns first
    cols_to_drop = []
    for i in range(1, 31):
        base = f"Phone {i}"
        for suffix in ("", " Status", " Type", " Tag"):
            col = f"Phone{suffix} {i}" if suffix else base
            if col in cleaned_df.columns:
                cols_to_drop.append(col)
    cleaned_df.drop(columns=[c for c in cols_to_drop if c in cleaned_df.columns], inplace=True)

    # Reinsert selected phones as Phone 1..N
    for idx, meta in enumerate(selected, start=1):
        cleaned_df[f"Phone {idx}"] = df[meta.column]

    return cleaned_df, selected
