"""Enhanced dialog showing phone prioritization preview with customization options."""
from __future__ import annotations

from typing import List, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, 
    QHBoxLayout, QLabel, QGroupBox, QGridLayout, QSpinBox, QComboBox,
    QScrollArea, QWidget, QSplitter, QFrame, QTextEdit, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from backend.utils.phone_prioritizer import PhoneMeta
import pandas as pd


class PhonePrioritizationDialog(QDialog):
    """Enhanced phone prioritization dialog with customization options."""
    
    # Signal emitted when prioritization rules change
    rules_changed = pyqtSignal(dict)
    
    def __init__(self, meta: List[PhoneMeta], source_df=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Phone Prioritization & Mapping Preview")
        self.resize(1200, 800)
        
        self.meta_all = meta
        self.source_df = source_df
        self.show_all = False
        
        # Default prioritization rules
        self.prioritization_rules = {
            'status_weights': {
                'CORRECT': 100,
                'UNKNOWN': 80,
                'NO_ANSWER': 60,
                'WRONG': 40,
                'DEAD': 20,
                'DNC': 10
            },
            'type_weights': {
                'MOBILE': 100,
                'LANDLINE': 80,
                'UNKNOWN': 60
            },
            'tag_weights': {
                'call_a01': 100,
                'call_a02': 90,
                'call_a03': 80,
                'call_a04': 70,
                'call_a05': 60,
                'no_tag': 50
            },
            'call_count_multiplier': 1.0
        }
        
        self._setup_ui()
        self._populate_mapping_preview()
        self._update_summary()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create splitter for left/right panels
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel: Prioritization rules
        left_panel = self._create_rules_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Mapping preview
        right_panel = self._create_preview_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
        # Bottom buttons
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Prioritization")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addStretch()
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.apply_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def _create_rules_panel(self) -> QWidget:
        """Create the left panel with prioritization rules."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("📞 Phone Prioritization Rules")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Scroll area for rules
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(600)
        
        rules_widget = QWidget()
        rules_layout = QVBoxLayout(rules_widget)
        
        # Status weights
        status_group = self._create_status_weights_group()
        rules_layout.addWidget(status_group)
        
        # Type weights
        type_group = self._create_type_weights_group()
        rules_layout.addWidget(type_group)
        
        # Tag weights
        tag_group = self._create_tag_weights_group()
        rules_layout.addWidget(tag_group)
        
        # Call count multiplier
        call_group = self._create_call_count_group()
        rules_layout.addWidget(call_group)
        
        # Preview button
        preview_btn = QPushButton("🔄 Update Preview")
        preview_btn.clicked.connect(self._update_preview_with_rules)
        rules_layout.addWidget(preview_btn)
        
        rules_layout.addStretch()
        scroll.setWidget(rules_widget)
        layout.addWidget(scroll)
        
        return panel
    
    def _create_status_weights_group(self) -> QGroupBox:
        """Create status weights configuration group."""
        group = QGroupBox("📊 Status Priority Weights")
        layout = QGridLayout(group)
        
        self.status_spinboxes = {}
        row = 0
        
        for status, weight in self.prioritization_rules['status_weights'].items():
            # Status label
            status_label = QLabel(f"{status}:")
            status_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(status_label, row, 0)
            
            # Weight spinbox
            spinbox = QSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setValue(weight)
            spinbox.valueChanged.connect(self._on_rule_changed)
            layout.addWidget(spinbox, row, 1)
            
            # Description
            desc = self._get_status_description(status)
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.addWidget(desc_label, row, 2)
            
            self.status_spinboxes[status] = spinbox
            row += 1
        
        return group
    
    def _create_type_weights_group(self) -> QGroupBox:
        """Create phone type weights configuration group."""
        group = QGroupBox("📱 Phone Type Priority Weights")
        layout = QGridLayout(group)
        
        self.type_spinboxes = {}
        row = 0
        
        for phone_type, weight in self.prioritization_rules['type_weights'].items():
            # Type label
            type_label = QLabel(f"{phone_type}:")
            type_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(type_label, row, 0)
            
            # Weight spinbox
            spinbox = QSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setValue(weight)
            spinbox.valueChanged.connect(self._on_rule_changed)
            layout.addWidget(spinbox, row, 1)
            
            # Description
            desc = self._get_type_description(phone_type)
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.addWidget(desc_label, row, 2)
            
            self.type_spinboxes[phone_type] = spinbox
            row += 1
        
        return group
    
    def _create_tag_weights_group(self) -> QGroupBox:
        """Create call tag weights configuration group."""
        group = QGroupBox("🏷️ Call Tag Priority Weights")
        layout = QGridLayout(group)
        
        self.tag_spinboxes = {}
        row = 0
        
        for tag, weight in self.prioritization_rules['tag_weights'].items():
            # Tag label
            tag_label = QLabel(f"{tag}:")
            tag_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(tag_label, row, 0)
            
            # Weight spinbox
            spinbox = QSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setValue(weight)
            spinbox.valueChanged.connect(self._on_rule_changed)
            layout.addWidget(spinbox, row, 1)
            
            # Description
            desc = self._get_tag_description(tag)
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.addWidget(desc_label, row, 2)
            
            self.tag_spinboxes[tag] = spinbox
            row += 1
        
        return group
    
    def _create_call_count_group(self) -> QGroupBox:
        """Create call count multiplier configuration group."""
        group = QGroupBox("📈 Call Count Multiplier")
        layout = QGridLayout(group)
        
        # Multiplier spinbox
        self.call_multiplier_spinbox = QSpinBox()
        self.call_multiplier_spinbox.setRange(0, 10)
        self.call_multiplier_spinbox.setValue(int(self.prioritization_rules['call_count_multiplier'] * 10))
        self.call_multiplier_spinbox.setSuffix(" / 10")
        self.call_multiplier_spinbox.valueChanged.connect(self._on_rule_changed)
        layout.addWidget(QLabel("Multiplier:"), 0, 0)
        layout.addWidget(self.call_multiplier_spinbox, 0, 1)
        
        # Description
        desc = QLabel("Higher values give more weight to phones with more call history")
        desc.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(desc, 1, 0, 1, 2)
        
        return group
    
    def _create_preview_panel(self) -> QWidget:
        """Create the right panel with mapping preview."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("📋 Phone Mapping Preview")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Summary text
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)
        
        # Mapping table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Phone Position", "Original Column", "Number", "Tag", "Status", "Type", "Call Cnt", "Priority Score"
        ])
        layout.addWidget(self.table)
        
        # Toggle button
        self.toggle_btn = QPushButton("Show Top 5")
        self.toggle_btn.clicked.connect(self._toggle_rows)
        layout.addWidget(self.toggle_btn)
        
        return panel
    
    def _get_status_description(self, status: str) -> str:
        """Get description for phone status."""
        descriptions = {
            'CORRECT': 'Verified working number',
            'UNKNOWN': 'Status not determined',
            'NO_ANSWER': 'No answer when called',
            'WRONG': 'Wrong number',
            'DEAD': 'Number disconnected',
            'DNC': 'Do not call list'
        }
        return descriptions.get(status, '')
    
    def _get_type_description(self, phone_type: str) -> str:
        """Get description for phone type."""
        descriptions = {
            'MOBILE': 'Mobile phone number',
            'LANDLINE': 'Landline phone number',
            'UNKNOWN': 'Type not determined'
        }
        return descriptions.get(phone_type, '')
    
    def _get_tag_description(self, tag: str) -> str:
        """Get description for call tag."""
        descriptions = {
            'call_a01': 'Most recent call',
            'call_a02': 'Second most recent',
            'call_a03': 'Third most recent',
            'call_a04': 'Fourth most recent',
            'call_a05': 'Fifth most recent',
            'no_tag': 'No call history'
        }
        return descriptions.get(tag, '')
    
    def _on_rule_changed(self):
        """Handle when prioritization rules change."""
        # Update rules from UI
        self._update_rules_from_ui()
        
        # Emit signal
        self.rules_changed.emit(self.prioritization_rules)
    
    def _update_rules_from_ui(self):
        """Update prioritization rules from UI controls."""
        # Status weights
        for status, spinbox in self.status_spinboxes.items():
            self.prioritization_rules['status_weights'][status] = spinbox.value()
        
        # Type weights
        for phone_type, spinbox in self.type_spinboxes.items():
            self.prioritization_rules['type_weights'][phone_type] = spinbox.value()
        
        # Tag weights
        for tag, spinbox in self.tag_spinboxes.items():
            self.prioritization_rules['tag_weights'][tag] = spinbox.value()
        
        # Call count multiplier
        self.prioritization_rules['call_count_multiplier'] = self.call_multiplier_spinbox.value() / 10.0
    
    def _update_preview_with_rules(self):
        """Update the preview based on current rules."""
        self._update_rules_from_ui()
        self._populate_mapping_preview()
        self._update_summary()
    
    def _populate_mapping_preview(self):
        """Populate the mapping preview table."""
        # Get current rules
        self._update_rules_from_ui()
        
        # Recalculate priorities based on rules
        recalculated_meta = self._recalculate_priorities()
        
        # Sort by priority
        recalculated_meta.sort(key=lambda x: x.priority, reverse=True)
        
        # Show top 5 or all
        rows_to_show = recalculated_meta if self.show_all else recalculated_meta[:5]
        
        self.table.setRowCount(len(rows_to_show))
        
        for row, m in enumerate(rows_to_show):
            # Phone position (Phone 1, Phone 2, etc.)
            position = f"Phone {row + 1}" if row < 5 else f"Excluded"
            self.table.setItem(row, 0, QTableWidgetItem(position))
            
            # Original column
            self.table.setItem(row, 1, QTableWidgetItem(m.column))
            
            # Number
            number_item = QTableWidgetItem(m.number)
            if not m.number.strip():
                number_item.setBackground(QColor(255, 240, 240))  # Light red for empty
            self.table.setItem(row, 2, number_item)
            
            # Tag
            tag_item = QTableWidgetItem(m.tag)
            if m.tag and m.tag != 'no_tag':
                tag_item.setBackground(QColor(240, 255, 240))  # Light green for tags
            self.table.setItem(row, 3, tag_item)
            
            # Status
            status_item = QTableWidgetItem(m.status)
            status_color = self._get_status_color(m.status)
            status_item.setBackground(status_color)
            self.table.setItem(row, 4, status_item)
            
            # Type
            type_item = QTableWidgetItem(m.phone_type)
            if m.phone_type == 'MOBILE':
                type_item.setBackground(QColor(240, 240, 255))  # Light blue for mobile
            self.table.setItem(row, 5, type_item)
            
            # Call count
            call_item = QTableWidgetItem(str(m.call_count))
            if m.call_count > 0:
                call_item.setBackground(QColor(255, 255, 240))  # Light yellow for calls
            self.table.setItem(row, 6, call_item)
            
            # Priority score
            priority_item = QTableWidgetItem(f"{m.priority:.1f}")
            priority_item.setBackground(self._get_priority_color(m.priority))
            self.table.setItem(row, 7, priority_item)
        
        self.table.resizeColumnsToContents()
    
    def _recalculate_priorities(self) -> List[PhoneMeta]:
        """Recalculate priorities based on current rules."""
        recalculated = []
        
        for meta in self.meta_all:
            # Calculate new priority based on rules
            priority = self._calculate_priority(meta)
            
            # Create new PhoneMeta with recalculated priority
            new_meta = PhoneMeta(
                column=meta.column,
                number=meta.number,
                tag=meta.tag,
                status=meta.status,
                phone_type=meta.phone_type,
                call_count=meta.call_count,
                priority=priority
            )
            recalculated.append(new_meta)
        
        return recalculated
    
    def _calculate_priority(self, meta: PhoneMeta) -> float:
        """Calculate priority score based on current rules."""
        score = 0.0
        
        # Status weight
        status_weight = self.prioritization_rules['status_weights'].get(meta.status, 0)
        score += status_weight
        
        # Type weight
        type_weight = self.prioritization_rules['type_weights'].get(meta.phone_type, 0)
        score += type_weight
        
        # Tag weight
        tag = meta.tag if meta.tag else 'no_tag'
        tag_weight = self.prioritization_rules['tag_weights'].get(tag, 0)
        score += tag_weight
        
        # Call count bonus
        call_bonus = meta.call_count * self.prioritization_rules['call_count_multiplier']
        score += call_bonus
        
        return score
    
    def _get_status_color(self, status: str) -> QColor:
        """Get background color for status."""
        colors = {
            'CORRECT': QColor(200, 255, 200),  # Light green
            'UNKNOWN': QColor(255, 255, 200),  # Light yellow
            'NO_ANSWER': QColor(255, 200, 200),  # Light red
            'WRONG': QColor(255, 150, 150),  # Red
            'DEAD': QColor(200, 200, 200),  # Gray
            'DNC': QColor(150, 150, 150)  # Dark gray
        }
        return colors.get(status, QColor(255, 255, 255))
    
    def _get_priority_color(self, priority: float) -> QColor:
        """Get background color for priority score."""
        if priority >= 200:
            return QColor(200, 255, 200)  # Green for high priority
        elif priority >= 150:
            return QColor(255, 255, 200)  # Yellow for medium priority
        elif priority >= 100:
            return QColor(255, 200, 200)  # Light red for low priority
        else:
            return QColor(255, 150, 150)  # Red for very low priority
    
    def _update_summary(self):
        """Update the summary text."""
        if not self.meta_all:
            self.summary_text.setPlainText("No phone data available.")
            return
        
        # Recalculate priorities
        recalculated_meta = self._recalculate_priorities()
        recalculated_meta.sort(key=lambda x: x.priority, reverse=True)
        
        # Get top 5 phones
        top_5 = recalculated_meta[:5]
        
        # Build summary
        summary_lines = []
        summary_lines.append("📊 PHONE MAPPING SUMMARY")
        summary_lines.append("=" * 50)
        summary_lines.append("")
        
        # Show how phones are mapped to Phone 1-5
        summary_lines.append("🎯 TOP 5 PHONES (Phone 1-5):")
        for i, meta in enumerate(top_5, 1):
            status_desc = self._get_status_description(meta.status)
            type_desc = self._get_type_description(meta.phone_type)
            tag_desc = self._get_tag_description(meta.tag) if meta.tag else "No call history"
            
            summary_lines.append(f"  Phone {i}: {meta.number} ({meta.column})")
            summary_lines.append(f"    Status: {meta.status} - {status_desc}")
            summary_lines.append(f"    Type: {meta.phone_type} - {type_desc}")
            summary_lines.append(f"    Tag: {meta.tag} - {tag_desc}")
            summary_lines.append(f"    Priority Score: {meta.priority:.1f}")
            summary_lines.append("")
        
        # Show statistics
        if self.source_df is not None:
            summary_lines.append("📈 STATISTICS:")
            stat_series = (
                self.source_df.filter(regex=r"^Phone Status ")
                .stack()
                .dropna()
                .astype(str)
                .str.upper()
            )
            total_phones = len(stat_series)
            counts = stat_series.value_counts()
            
            summary_lines.append(f"  Total phone entries: {total_phones:,}")
            for status in ["CORRECT", "UNKNOWN", "NO_ANSWER", "WRONG", "DEAD", "DNC"]:
                if status in counts:
                    count = int(counts[status])
                    percentage = (count / total_phones) * 100
                    summary_lines.append(f"  {status}: {count:,} ({percentage:.1f}%)")
        
        self.summary_text.setPlainText("\n".join(summary_lines))
    
    def _toggle_rows(self):
        """Toggle between showing top 5 and all rows."""
        self.show_all = not self.show_all
        self._populate_mapping_preview()
        self.toggle_btn.setText("Show Top 5" if self.show_all else "Show All")
    
    def get_prioritization_rules(self) -> Dict[str, Any]:
        """Get the current prioritization rules."""
        self._update_rules_from_ui()
        return self.prioritization_rules.copy()
