"""GUI tests for PhonePrioritizationDialog.

Requires pytest-qt. Verifies:
1. Initial view shows top-5 rows.
2. Toggle button switches to full list and back.
"""
from __future__ import annotations

from typing import List

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from backend.utils.phone_prioritizer import PhoneMeta
from frontend.dialogs.phone_prioritization_dialog import PhonePrioritizationDialog

# Ensure a QApplication exists (pytest-qt usually provides one via the qtbot fixture)
app = QApplication.instance() or QApplication([])  # pragma: no cover


@pytest.fixture()
def sample_meta() -> List[PhoneMeta]:
    """Create 10 fake PhoneMeta objects with descending priorities."""
    meta: List[PhoneMeta] = []
    for idx in range(10):
        meta.append(
            PhoneMeta(
                column=f"Phone {idx+1}",
                number=str(5550000000 + idx),
                tag="call_a00",
                status="UNKNOWN",
                phone_type="MOBILE",
                call_count=0,
                priority=100 - idx,
            )
        )
    return meta


def test_dialog_toggle_rows(qtbot, sample_meta):
    """Toggling the button should switch between 5-row and full-row views."""
    dlg = PhonePrioritizationDialog(sample_meta, None)
    qtbot.addWidget(dlg)
    dlg.show()

    assert dlg.table.rowCount() == 5  # default top-5

    # Click toggle → show all 10
    qtbot.mouseClick(dlg.toggle_btn, Qt.LeftButton)
    qtbot.waitUntil(lambda: dlg.table.rowCount() == len(sample_meta))

    # Click again → back to 5
    qtbot.mouseClick(dlg.toggle_btn, Qt.LeftButton)
    qtbot.waitUntil(lambda: dlg.table.rowCount() == 5)
