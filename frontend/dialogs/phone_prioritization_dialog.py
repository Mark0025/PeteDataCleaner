"""Dialog showing phone prioritization preview."""
from __future__ import annotations

from typing import List
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from backend.utils.phone_prioritizer import PhoneMeta


class PhonePrioritizationDialog(QDialog):
    def __init__(self, meta: List[PhoneMeta], source_df=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Phone Prioritization Preview")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        self.show_all = False  # start with top 5
        self.meta_all = meta
        self.source_df = source_df
        rows_to_show = meta if self.show_all else meta[:5]
        table = QTableWidget(len(rows_to_show), 7)
        table.setHorizontalHeaderLabels([
            "Original Column", "Number", "Tag", "Status", "Type", "Call Cnt", "Priority",
        ])
        for row, m in enumerate(rows_to_show):
            table.setItem(row, 0, QTableWidgetItem(m.column))
            table.setItem(row, 1, QTableWidgetItem(m.number))
            table.setItem(row, 2, QTableWidgetItem(m.tag))
            table.setItem(row, 3, QTableWidgetItem(m.status))
            table.setItem(row, 4, QTableWidgetItem(m.phone_type))
            table.setItem(row, 5, QTableWidgetItem(str(m.call_count)))
            table.setItem(row, 6, QTableWidgetItem(str(m.priority)))
        
        table.resizeColumnsToContents()
        self.table = table
        self.meta = meta
        layout.addWidget(table)
        # Toggle button to show all 30 or top 5
        self.toggle_btn = QPushButton("Show All 30")
        layout.addWidget(self.toggle_btn)
        self.toggle_btn.clicked.connect(self._toggle_rows)

        # Descriptive summary -------------------------------------------
        from PyQt5.QtWidgets import QLabel
        summary_lbl = QLabel(self._build_summary())
        summary_lbl.setWordWrap(True)
        layout.addWidget(summary_lbl)

        btn_box = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        btn_box.addStretch()
        btn_box.addWidget(self.apply_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)

        self.apply_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        # Methods ---------------------------------------------------
    def _build_summary(self) -> str:
        """Return human-readable description of what will happen."""
        if self.source_df is None:
            return "Status counts: N/A"
        import pandas as pd
        stat_series = (
            self.source_df.filter(regex=r"^Phone Status ")
            .stack()
            .dropna()
            .astype(str)
            .str.upper()
        )
        total_phones = len(stat_series)
        counts = stat_series.value_counts()
        parts = []
        for key in ("CORRECT", "UNKNOWN", "NO_ANSWER", "WRONG", "DEAD", "DNC"):
            if key in counts:
                parts.append(f"{key}: {int(counts[key])}")
        if not parts:
            return "No status information found; prioritisation will use column order and phone type only."
        summary = (
            f"Detected {total_phones} phone entries – " + ", ".join(parts) +
            ".  CORRECT numbers will move to Phone 1-5; WRONG/DEAD/DNC numbers will be excluded."
        )
        return summary

    def _toggle_rows(self):
        """Toggle between showing top 5 and all 30 rows."""
        self.show_all = not self.show_all
        rows_to_show = self.meta_all if self.show_all else self.meta_all[:5]
        self.table.setRowCount(len(rows_to_show))
        for row, m in enumerate(rows_to_show):
            self.table.setItem(row, 0, QTableWidgetItem(m.column))
            self.table.setItem(row, 1, QTableWidgetItem(m.number))
            self.table.setItem(row, 2, QTableWidgetItem(m.tag))
            self.table.setItem(row, 3, QTableWidgetItem(m.status))
            self.table.setItem(row, 4, QTableWidgetItem(m.phone_type))
            self.table.setItem(row, 5, QTableWidgetItem(str(m.call_count)))
            self.table.setItem(row, 6, QTableWidgetItem(str(m.priority)))
        self.toggle_btn.setText("Show Top 5" if self.show_all else "Show All 30")
        self.table.resizeColumnsToContents()
