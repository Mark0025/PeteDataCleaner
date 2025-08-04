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
    tag: str
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


from backend.utils.phone_processor import PhoneProcessor


def prioritize(df: pd.DataFrame, max_phones: int = 5) -> Tuple[pd.DataFrame, List[PhoneMeta]]:
    """Prioritize phones row-by-row and return *(clean_df, meta_list)*.

    The cleaned DataFrame contains up to *max_phones* ``Phone N`` columns
    reordered per record using :class:`backend.utils.phone_processor.PhoneProcessor`.

    The returned ``meta_list`` is a global summary of the original phone columns
    ranked by their **aggregate** priority across the whole dataset (highest
    priority first).  This list is used purely for preview in the GUI dialog
    and therefore does **not** need row-level granularity.
    """

    # --- 1.  Apply per-row allocation using PhoneProcessor -----------------
    processor = PhoneProcessor()
    cleaned_df = processor.reorder_phone_allocation(df, max_phones=max_phones)

    # --- 2.  Build preview metadata aggregated over the dataset -------------
    phone_entries: List[PhoneMeta] = []
    for i in range(1, 31):
        col = f"Phone {i}"
        if col not in df.columns:
            continue

        # Determine the most common status / type values for this column
        status_series = df.get(f"Phone Status {i}")
        status_val = (
            status_series.mode().iat[0] if status_series is not None and not status_series.empty else "UNKNOWN"
        )
        type_series = df.get(f"Phone Type {i}")
        type_val = (
            type_series.mode().iat[0] if type_series is not None and not type_series.empty else "UNKNOWN"
        )
        tag_series = df.get(f"Phone Tag {i}")
        tag_val = (
            tag_series.mode().iat[0] if tag_series is not None and not tag_series.empty else ""
        )

        status_key = str(status_val).upper() if status_val else "UNKNOWN"
        type_key = str(type_val).upper() if type_val else "UNKNOWN"
        call_count = _extract_call_count(str(tag_val))

        base = STATUS_WEIGHT.get(status_key, 0)
        bonus = TYPE_BONUS.get(type_key, 0)
        score = base + bonus - (call_count * CALL_COUNT_PENALTY) - i  # earlier cols slightly preferred

        phone_entries.append(
            PhoneMeta(
                column=col,
                number=str(df[col].iloc[0]) if col in df.columns else "",
                tag=str(tag_val),
                status=status_key,
                phone_type=type_key,
                call_count=call_count,
                priority=score,
            )
        )

    phone_entries.sort(key=lambda p: p.priority, reverse=True)
    selected_meta = phone_entries[:max_phones]

    return cleaned_df, selected_meta
