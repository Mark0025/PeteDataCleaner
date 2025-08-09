#!/usr/bin/env python3
"""
Custom Export UI

Advanced export interface for investor analysis with customizable headers,
export presets, and comprehensive data export capabilities.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QComboBox, QCheckBox, QGroupBox, QScrollArea,
    QWidget, QFrame, QTextEdit, QLineEdit, QMessageBox,
    QProgressBar, QSplitter, QTabWidget, QInputDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

from .export_config import ExportConfig, ExportPreset
from .header_selector import HeaderSelector
from .export_preview import ExportPreview


class CustomExportUI(QDialog):
    """Main custom export interface."""
    
    def __init__(self, parent=None, owner_objects=None, enhanced_data=None):
        super().__init__(parent)
        
        self.owner_objects = owner_objects or []
        self.enhanced_data = enhanced_data
        self.export_config = ExportConfig()
        self.selected_headers = []
        self.current_preset = None
        
        self.setup_ui()
        self.load_default_preset()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("🎯 Custom Export Tool - Investor Analysis")
        self.setMinimumSize(1000, 700)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🎯 Custom Export Tool - Investor Analysis")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #667eea; margin: 10px;")
        main_layout.addWidget(header, alignment=Qt.AlignCenter)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Tab 1: Export Configuration
        config_tab = self.create_config_tab()
        tab_widget.addTab(config_tab, "📋 Export Configuration")
        
        # Tab 2: Header Selection
        header_tab = self.create_header_tab()
        tab_widget.addTab(header_tab, "📊 Header Selection")
        
        # Tab 3: Preview
        preview_tab = self.create_preview_tab()
        tab_widget.addTab(preview_tab, "👁️ Preview")
        
        main_layout.addWidget(tab_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("📤 Export")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.export_btn.clicked.connect(self.export_data)
        
        self.save_preset_btn = QPushButton("💾 Save Preset")
        self.save_preset_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.save_preset_btn.clicked.connect(self.save_custom_preset)
        
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.save_preset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_config_tab(self) -> QWidget:
        """Create the export configuration tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Export Preset Selection
        preset_group = QGroupBox("📋 Export Preset")
        preset_layout = QVBoxLayout(preset_group)
        
        # Preset dropdown
        preset_layout.addWidget(QLabel("Select Export Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        # Load presets
        presets = self.export_config.list_presets()
        for name, preset in presets.items():
            self.preset_combo.addItem(f"{preset.name} - {preset.description}", name)
        
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)
        
        # Preset info
        self.preset_info = QTextEdit()
        self.preset_info.setMaximumHeight(100)
        self.preset_info.setReadOnly(True)
        self.preset_info.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        preset_layout.addWidget(self.preset_info)
        
        layout.addWidget(preset_group)
        
        # Export Format
        format_group = QGroupBox("📁 Export Format")
        format_layout = QHBoxLayout(format_group)
        
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "Excel", "JSON"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        
        layout.addWidget(format_group)
        
        # Filters
        filter_group = QGroupBox("🔍 Filters")
        filter_layout = QGridLayout(filter_group)
        
        # Owner type filter
        filter_layout.addWidget(QLabel("Owner Type:"), 0, 0)
        self.owner_type_combo = QComboBox()
        self.owner_type_combo.addItems(["All", "Individual", "Business"])
        filter_layout.addWidget(self.owner_type_combo, 0, 1)
        
        # Phone quality filter
        filter_layout.addWidget(QLabel("Phone Quality:"), 1, 0)
        self.phone_quality_combo = QComboBox()
        self.phone_quality_combo.addItems(["All", "High (8.0+)", "Medium (6.0-8.0)", "Low (<6.0)"])
        filter_layout.addWidget(self.phone_quality_combo, 1, 1)
        
        # Phone status filter
        filter_layout.addWidget(QLabel("Phone Status:"), 2, 0)
        self.phone_status_combo = QComboBox()
        self.phone_status_combo.addItems(["All", "CORRECT", "UNKNOWN", "NO_ANSWER", "WRONG", "DEAD"])
        filter_layout.addWidget(self.phone_status_combo, 2, 1)
        
        layout.addWidget(filter_group)
        
        # Summary
        summary_group = QGroupBox("📊 Export Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(120)
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        layout.addStretch()
        
        return widget
    
    def create_header_tab(self) -> QWidget:
        """Create the header selection tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Header selector
        self.header_selector = HeaderSelector(self.export_config)
        self.header_selector.headers_changed.connect(self.on_headers_changed)
        layout.addWidget(self.header_selector)
        
        return widget
    
    def create_preview_tab(self) -> QWidget:
        """Create the preview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Preview controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Preview")
        refresh_btn.clicked.connect(self.refresh_preview)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Preview widget
        self.preview_widget = ExportPreview()
        layout.addWidget(self.preview_widget)
        
        return widget
    
    def load_default_preset(self):
        """Load the default Pete preset."""
        self.preset_combo.setCurrentText("Pete CRM Export - Standard export for Pete CRM integration with prioritized phones")
        self.on_preset_changed()
    
    def on_preset_changed(self):
        """Handle preset selection change."""
        current_index = self.preset_combo.currentIndex()
        if current_index >= 0:
            preset_name = self.preset_combo.itemData(current_index)
            preset = self.export_config.get_preset(preset_name)
            
            if preset:
                self.current_preset = preset
                self.selected_headers = preset.headers.copy()
                
                # Update preset info
                info_text = f"""
Preset: {preset.name}
Description: {preset.description}
Headers: {len(preset.headers)} selected
Format: {preset.format.upper()}
Include Metadata: {'Yes' if preset.include_metadata else 'No'}

Selected Headers:
{', '.join(preset.headers[:10])}{'...' if len(preset.headers) > 10 else ''}
                """.strip()
                
                self.preset_info.setText(info_text)
                
                # Update header selector
                if hasattr(self, 'header_selector'):
                    self.header_selector.set_selected_headers(preset.headers)
                
                # Update format
                format_index = self.format_combo.findText(preset.format.upper())
                if format_index >= 0:
                    self.format_combo.setCurrentIndex(format_index)
                
                self.update_summary()
    
    def on_headers_changed(self, headers: List[str]):
        """Handle header selection change."""
        self.selected_headers = headers
        self.update_summary()
    
    def update_summary(self):
        """Update the export summary."""
        if not self.owner_objects:
            summary = "No owner data available for export."
        else:
            total_owners = len(self.owner_objects)
            format_name = self.format_combo.currentText()
            header_count = len(self.selected_headers)
            
            # Apply filters
            filtered_count = self.apply_filters(self.owner_objects)
            
            summary = f"""
Export Summary:
• Total Owners: {total_owners:,}
• Filtered Owners: {filtered_count:,}
• Selected Headers: {header_count}
• Export Format: {format_name}
• Estimated File Size: {self.estimate_file_size(filtered_count, header_count):.1f} MB

Ready to export {filtered_count:,} records with {header_count} columns.
            """.strip()
        
        self.summary_text.setText(summary)
    
    def apply_filters(self, owners: List) -> int:
        """Apply current filters to owner objects."""
        filtered_count = 0
        
        for owner in owners:
            # Owner type filter
            owner_type = self.owner_type_combo.currentText()
            if owner_type != "All":
                if owner_type == "Individual" and not owner.is_individual_owner:
                    continue
                if owner_type == "Business" and not owner.is_business_owner:
                    continue
            
            # Phone quality filter
            quality_filter = self.phone_quality_combo.currentText()
            if quality_filter != "All":
                if quality_filter == "High (8.0+)" and owner.phone_quality_score < 8.0:
                    continue
                elif quality_filter == "Medium (6.0-8.0)" and (owner.phone_quality_score < 6.0 or owner.phone_quality_score >= 8.0):
                    continue
                elif quality_filter == "Low (<6.0)" and owner.phone_quality_score >= 6.0:
                    continue
            
            # Phone status filter
            status_filter = self.phone_status_combo.currentText()
            if status_filter != "All":
                has_status = False
                for phone in owner.all_phones:
                    if phone.status == status_filter:
                        has_status = True
                        break
                if not has_status:
                    continue
            
            filtered_count += 1
        
        return filtered_count
    
    def estimate_file_size(self, record_count: int, column_count: int) -> float:
        """Estimate file size in MB."""
        # Rough estimate: 100 bytes per field
        bytes_per_record = column_count * 100
        total_bytes = record_count * bytes_per_record
        return total_bytes / (1024 * 1024)  # Convert to MB
    
    def refresh_preview(self):
        """Refresh the export preview."""
        if not self.owner_objects or not self.selected_headers:
            return
        
        # Create sample data for preview
        sample_owners = self.owner_objects[:10]  # First 10 owners
        preview_data = self.create_export_data(sample_owners)
        
        if preview_data:
            self.preview_widget.set_data(preview_data)
    
    def create_export_data(self, owners: List) -> Optional[pd.DataFrame]:
        """Create export data from owner objects."""
        if not owners or not self.selected_headers:
            return None
        
        export_data = []
        
        for owner in owners:
            row = {}
            
            for header in self.selected_headers:
                value = self.get_header_value(owner, header)
                row[header] = value
            
            export_data.append(row)
        
        return pd.DataFrame(export_data)
    
    def get_header_value(self, owner, header: str) -> Any:
        """Get value for a specific header from owner object."""
        # Map header names to owner object attributes
        header_mapping = {
            'Property Address': owner.property_address,
            'Mailing Address': owner.mailing_address,
            'Owner Name': owner.seller1_name,
            'Owner Type': 'Business' if owner.is_business_owner else 'Individual',
            'Phone Quality Score': owner.phone_quality_score,
            'Best Contact Method': owner.best_contact_method,
            'Skip Trace Target': owner.skip_trace_target,
            'Property Count': owner.property_count,
            'Total Property Value': owner.total_property_value,
            'LLC Analysis': str(owner.llc_analysis.get('business_type', 'Individual')),
            'Contact Quality': owner.llc_analysis.get('contact_quality', 'Unknown'),
            'Confidence Score': owner.confidence_score
        }
        
        # Handle phone headers
        if header.startswith('Phone 1 (Pete)') and owner.pete_prioritized_phones:
            return owner.pete_prioritized_phones[0].number if len(owner.pete_prioritized_phones) > 0 else ""
        elif header.startswith('Phone 2 (Pete)') and len(owner.pete_prioritized_phones) > 1:
            return owner.pete_prioritized_phones[1].number
        elif header.startswith('Phone 3 (Pete)') and len(owner.pete_prioritized_phones) > 2:
            return owner.pete_prioritized_phones[2].number
        elif header.startswith('Phone 4 (Pete)') and len(owner.pete_prioritized_phones) > 3:
            return owner.pete_prioritized_phones[3].number
        
        # Handle original phone headers
        for i in range(5, 11):
            if header.startswith(f'Phone {i} (Original)') and len(owner.all_phones) > i-1:
                return owner.all_phones[i-1].number if i-1 < len(owner.all_phones) else ""
        
        # Handle phone metadata headers
        if header.startswith('Phone Status 1') and owner.pete_prioritized_phones:
            return owner.pete_prioritized_phones[0].status if len(owner.pete_prioritized_phones) > 0 else ""
        elif header.startswith('Phone Type 1') and owner.pete_prioritized_phones:
            return owner.pete_prioritized_phones[0].phone_type if len(owner.pete_prioritized_phones) > 0 else ""
        elif header.startswith('Phone Tags 1') and owner.pete_prioritized_phones:
            return owner.pete_prioritized_phones[0].tags if len(owner.pete_prioritized_phones) > 0 else ""
        
        # Return mapped value or empty string
        return header_mapping.get(header, "")
    
    def export_data(self):
        """Export the data."""
        if not self.owner_objects:
            QMessageBox.warning(self, "No Data", "No owner data available for export.")
            return
        
        if not self.selected_headers:
            QMessageBox.warning(self, "No Headers", "Please select at least one header for export.")
            return
        
        # Apply filters
        filtered_owners = []
        for owner in self.owner_objects:
            # Apply the same filters as in apply_filters
            owner_type = self.owner_type_combo.currentText()
            if owner_type != "All":
                if owner_type == "Individual" and not owner.is_individual_owner:
                    continue
                if owner_type == "Business" and not owner.is_business_owner:
                    continue
            
            quality_filter = self.phone_quality_combo.currentText()
            if quality_filter != "All":
                if quality_filter == "High (8.0+)" and owner.phone_quality_score < 8.0:
                    continue
                elif quality_filter == "Medium (6.0-8.0)" and (owner.phone_quality_score < 6.0 or owner.phone_quality_score >= 8.0):
                    continue
                elif quality_filter == "Low (<6.0)" and owner.phone_quality_score >= 6.0:
                    continue
            
            status_filter = self.phone_status_combo.currentText()
            if status_filter != "All":
                has_status = False
                for phone in owner.all_phones:
                    if phone.status == status_filter:
                        has_status = True
                        break
                if not has_status:
                    continue
            
            filtered_owners.append(owner)
        
        if not filtered_owners:
            QMessageBox.warning(self, "No Data", "No data matches the selected filters.")
            return
        
        # Create export data
        export_df = self.create_export_data(filtered_owners)
        
        if export_df is None or export_df.empty:
            QMessageBox.warning(self, "Export Error", "Could not create export data.")
            return
        
        # Get export format
        export_format = self.format_combo.currentText().lower()
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        preset_name = self.current_preset.name if self.current_preset else "custom"
        filename = f"custom_export_{preset_name.lower().replace(' ', '_')}_{timestamp}"
        
        # Export
        try:
            export_dir = Path("data/exports")
            export_dir.mkdir(parents=True, exist_ok=True)
            
            if export_format == "csv":
                filepath = export_dir / f"{filename}.csv"
                export_df.to_csv(filepath, index=False)
            elif export_format == "excel":
                filepath = export_dir / f"{filename}.xlsx"
                export_df.to_excel(filepath, index=False)
            elif export_format == "json":
                filepath = export_dir / f"{filename}.json"
                export_df.to_json(filepath, orient='records', indent=2)
            
            QMessageBox.information(
                self, 
                "Export Complete", 
                f"Successfully exported {len(filtered_owners):,} records to:\n{filepath}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
    
    def save_custom_preset(self):
        """Save current configuration as a custom preset."""
        name, ok = QInputDialog.getText(self, "Save Preset", "Enter preset name:")
        if not ok or not name:
            return
        
        # Create custom preset
        custom_preset = ExportPreset(
            name=name,
            description=f"Custom export preset created on {datetime.now().strftime('%Y-%m-%d')}",
            headers=self.selected_headers,
            filters={
                'owner_type': self.owner_type_combo.currentText(),
                'phone_quality': self.phone_quality_combo.currentText(),
                'phone_status': self.phone_status_combo.currentText()
            },
            format=self.format_combo.currentText().lower(),
            include_metadata=True
        )
        
        # Save preset
        success = self.export_config.save_custom_preset(name.lower().replace(' ', '_'), custom_preset)
        
        if success:
            QMessageBox.information(self, "Preset Saved", f"Custom preset '{name}' saved successfully.")
            # Refresh preset list
            self.preset_combo.clear()
            presets = self.export_config.list_presets()
            for name, preset in presets.items():
                self.preset_combo.addItem(f"{preset.name} - {preset.description}", name)
        else:
            QMessageBox.warning(self, "Save Failed", "Failed to save custom preset.")


def test_custom_export_ui():
    """Test the custom export UI."""
    print("🧪 Testing Custom Export UI")
    print("=" * 50)
    
    # Create sample owner objects for testing
    from backend.utils.enhanced_owner_analyzer import EnhancedOwnerObject, PhoneData
    
    sample_owners = [
        EnhancedOwnerObject(
            seller1_name="John Doe",
            property_address="123 Main St",
            mailing_address="123 Main St",
            is_individual_owner=True,
            phone_quality_score=8.5,
            all_phones=[
                PhoneData(number="555-1234", status="CORRECT", phone_type="MOBILE"),
                PhoneData(number="555-5678", status="UNKNOWN", phone_type="LANDLINE")
            ],
            pete_prioritized_phones=[
                PhoneData(number="555-1234", status="CORRECT", phone_type="MOBILE", is_pete_prioritized=True)
            ]
        ),
        EnhancedOwnerObject(
            seller1_name="ABC Properties LLC",
            property_address="456 Oak Ave",
            mailing_address="789 Business Blvd",
            is_business_owner=True,
            phone_quality_score=6.2,
            all_phones=[
                PhoneData(number="555-9999", status="WRONG", phone_type="LANDLINE")
            ],
            pete_prioritized_phones=[
                PhoneData(number="555-9999", status="WRONG", phone_type="LANDLINE", is_pete_prioritized=True)
            ]
        )
    ]
    
    print(f"✅ Created {len(sample_owners)} sample owner objects")
    print(f"📊 Sample data ready for export UI testing")
    
    return sample_owners


if __name__ == "__main__":
    test_custom_export_ui() 