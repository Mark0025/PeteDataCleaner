"""Dialog showing phone prioritization preview."""
from __future__ import annotations

from typing import List
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from backend.utils.phone_prioritizer import PhoneMeta

class PhonePrioritizationDialog(QDialog):
    def __init__(self, meta: List[PhoneMeta], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Phone Prioritization Preview")
        self.resize(600, 400)

        layout = QVBoxLayout(self)
        table = QTableWidget(len(meta), 6)
        table.setHorizontalHeaderLabels([
            "Original Column", "Status", "Type", "Call Cnt", "Priority", "Pete Slot",
        ])
        for row, m in enumerate(meta):
            table.setItem(row, 0, QTableWidgetItem(m.column))
            table.setItem(row, 1, QTableWidgetItem(m.status))
            table.setItem(row, 2, QTableWidgetItem(m.phone_type))
            table.setItem(row, 3, QTableWidgetItem(str(m.call_count)))
            table.setItem(row, 4, QTableWidgetItem(str(m.priority)))
            pete_slot = str(row + 1) if row < 5 else "-"
            table.setItem(row, 5, QTableWidgetItem(pete_slot))
        table.resizeColumnsToContents()
        layout.addWidget(table)

        btn_box = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        btn_box.addStretch()
        btn_box.addWidget(self.apply_btn)
        btn_box.addWidget(self.cancel_btn)
        layout.addLayout(btn_box)

        self.apply_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        self.table = table
        self.meta = meta
