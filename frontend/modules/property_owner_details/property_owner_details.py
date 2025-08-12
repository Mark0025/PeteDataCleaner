#!/usr/bin/env python3
"""
Property Owner Details - Main Module

Shows comprehensive details about a specific owner including:
- All properties owned
- Phone numbers with status
- LLC analysis
- Contact methods
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QFrame, QScrollArea, QGroupBox,
    QHeaderView, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor
from typing import Any, List, Dict
import pandas as pd
from pathlib import Path

from backend.utils.efficient_table_manager import format_currency, format_phone_quality_pete, get_owner_name, get_owner_type, get_confidence_level, get_best_contact_method_pete
from backend.utils.cpu_monitor import monitor_cpu_usage


class PropertyOwnerDetails(QWidget):
    """Detailed view of a specific property owner."""
    
    def __init__(self, owner_object: Any, parent=None):
        super().__init__(parent)
        self.owner = owner_object
        self.setup_ui()
        self.populate_data()
    
    def setup_ui(self):
        """Setup the UI layout."""
        self.setWindowTitle(f"🏠 Property Owner Details - {get_owner_name(self.owner)}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"🏠 Property Owner Details - {get_owner_name(self.owner)}")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #667eea; margin: 10px;")
        main_layout.addWidget(header)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Owner Summary Section
        self.create_owner_summary(scroll_layout)
        
        # Properties Section
        self.create_properties_section(scroll_layout)
        
        # Phone Numbers Section
        self.create_phone_section(scroll_layout)
        
        # LLC Analysis Section (if applicable)
        if self.owner.is_business_owner:
            self.create_llc_analysis_section(scroll_layout)
        
        # Action Buttons
        self.create_action_buttons(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
    
    def create_owner_summary(self, layout):
        """Create owner summary section."""
        group = QGroupBox("📊 Owner Summary")
        group_layout = QVBoxLayout(group)
        
        # Summary grid
        summary_layout = QHBoxLayout()
        
        # Left column
        left_col = QVBoxLayout()
        
        # Owner Name
        name_label = QLabel(f"<b>Name:</b> {get_owner_name(self.owner)}")
        name_label.setStyleSheet("font-size: 14px; margin: 5px;")
        left_col.addWidget(name_label)
        
        # Owner Type
        type_label = QLabel(f"<b>Type:</b> {get_owner_type(self.owner)}")
        type_label.setStyleSheet("font-size: 14px; margin: 5px;")
        left_col.addWidget(type_label)
        
        # Mailing Address
        mailing_addr = self._get_mailing_address()
        addr_label = QLabel(f"<b>Mailing Address:</b> {mailing_addr}")
        addr_label.setStyleSheet("font-size: 14px; margin: 5px;")
        addr_label.setWordWrap(True)
        left_col.addWidget(addr_label)
        
        summary_layout.addLayout(left_col)
        
        # Right column
        right_col = QVBoxLayout()
        
        # Property Count
        count_label = QLabel(f"<b>Total Properties:</b> {self.owner.property_count:,}")
        count_label.setStyleSheet("font-size: 14px; margin: 5px;")
        right_col.addWidget(count_label)
        
        # Total Value
        value_label = QLabel(f"<b>Total Value:</b> {format_currency(self.owner.total_property_value, self.owner)}")
        value_label.setStyleSheet("font-size: 14px; margin: 5px;")
        right_col.addWidget(value_label)
        
        # Phone Quality
        quality_label = QLabel(f"<b>Phone Quality:</b> {format_phone_quality_pete(self.owner.phone_quality_score, self.owner)}")
        quality_label.setStyleSheet("font-size: 14px; margin: 5px;")
        right_col.addWidget(quality_label)
        
        # Best Contact Method
        contact_label = QLabel(f"<b>Best Contact:</b> {get_best_contact_method_pete(self.owner)}")
        contact_label.setStyleSheet("font-size: 14px; margin: 5px;")
        right_col.addWidget(contact_label)
        
        # Confidence
        confidence_label = QLabel(f"<b>Confidence:</b> {get_confidence_level(self.owner)}")
        confidence_label.setStyleSheet("font-size: 14px; margin: 5px;")
        right_col.addWidget(confidence_label)
        
        summary_layout.addLayout(right_col)
        
        group_layout.addLayout(summary_layout)
        layout.addWidget(group)
    
    def create_properties_section(self, layout):
        """Create properties owned section."""
        group = QGroupBox("📍 Properties Owned")
        group_layout = QVBoxLayout(group)
        
        # Properties table
        self.properties_table = QTableWidget()
        self.properties_table.setColumnCount(5)
        self.properties_table.setHorizontalHeaderLabels([
            "Property Address", "Mailing Address", "Value", "Type", "Phone Count"
        ])
        
        # Set table properties
        header = self.properties_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Property Address
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Mailing Address
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Value
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Phone Count
        
        self.properties_table.setAlternatingRowColors(True)
        self.properties_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        group_layout.addWidget(self.properties_table)
        layout.addWidget(group)
    
    def create_phone_section(self, layout):
        """Create phone numbers section."""
        group = QGroupBox("📞 Phone Numbers Available")
        group_layout = QVBoxLayout(group)
        
        # Phone numbers table
        self.phones_table = QTableWidget()
        self.phones_table.setColumnCount(7)
        self.phones_table.setHorizontalHeaderLabels([
            "Number", "Status", "Type", "Priority", "Tags", "Confidence", "Original Column"
        ])
        
        # Set table properties
        header = self.phones_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Number
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Priority
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Tags
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Confidence
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Original Column
        
        self.phones_table.setAlternatingRowColors(True)
        self.phones_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        group_layout.addWidget(self.phones_table)
        layout.addWidget(group)
    
    def create_llc_analysis_section(self, layout):
        """Create LLC analysis section."""
        group = QGroupBox("🏢 LLC Analysis")
        group_layout = QVBoxLayout(group)
        
        # LLC analysis content
        if hasattr(self.owner, 'llc_analysis') and self.owner.llc_analysis:
            llc_data = self.owner.llc_analysis
            
            # Business name
            if 'business_name' in llc_data:
                business_label = QLabel(f"<b>Business Name:</b> {llc_data['business_name']}")
                business_label.setStyleSheet("font-size: 14px; margin: 5px;")
                group_layout.addWidget(business_label)
            
            # Business type
            if 'business_type' in llc_data:
                type_label = QLabel(f"<b>Business Type:</b> {llc_data['business_type']}")
                type_label.setStyleSheet("font-size: 14px; margin: 5px;")
                group_layout.addWidget(type_label)
            
            # Owner identification
            if 'owner_identified' in llc_data:
                owner_label = QLabel(f"<b>Owner Identified:</b> {'Yes' if llc_data['owner_identified'] else 'No'}")
                owner_label.setStyleSheet("font-size: 14px; margin: 5px;")
                group_layout.addWidget(owner_label)
            
            # Contact methods
            if 'contact_methods' in llc_data:
                contact_label = QLabel(f"<b>Contact Methods:</b> {', '.join(llc_data['contact_methods'])}")
                contact_label.setStyleSheet("font-size: 14px; margin: 5px;")
                group_layout.addWidget(contact_label)
        else:
            # No LLC analysis data
            no_data_label = QLabel("No LLC analysis data available")
            no_data_label.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
            group_layout.addWidget(no_data_label)
        
        layout.addWidget(group)
    
    def create_action_buttons(self, layout):
        """Create action buttons."""
        button_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd8;
            }
        """)
        back_btn.clicked.connect(self.close)
        button_layout.addWidget(back_btn)
        
        # Export button
        export_btn = QPushButton("📊 Export Owner Data")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        export_btn.clicked.connect(self.export_owner_data)
        button_layout.addWidget(export_btn)
        
        # Skip trace button
        skip_trace_btn = QPushButton("🔍 Skip Trace")
        skip_trace_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        skip_trace_btn.clicked.connect(self.skip_trace)
        button_layout.addWidget(skip_trace_btn)
        
        layout.addLayout(button_layout)
    
    @monitor_cpu_usage
    def populate_data(self):
        """Populate all data sections."""
        self.populate_properties_table()
        self.populate_phones_table()
    
    @monitor_cpu_usage
    def populate_properties_table(self):
        """Populate properties table."""
        properties = []
        
        # Get properties from property_details
        if hasattr(self.owner, 'property_details') and self.owner.property_details:
            properties = self.owner.property_details
        else:
            # Fallback: create property objects from addresses
            if hasattr(self.owner, 'property_addresses') and self.owner.property_addresses:
                for addr in self.owner.property_addresses:
                    # Create a simple property object
                    class SimpleProperty:
                        def __init__(self, address):
                            self.property_address = address
                            self.mailing_address = self.owner.mailing_address
                            self.property_value = self.owner.total_property_value / max(self.owner.property_count, 1)
                            self.owner_type = get_owner_type(self.owner)
                            self.phone_numbers = self.owner.all_phones if hasattr(self.owner, 'all_phones') else []
                    
                    properties.append(SimpleProperty(addr))
        
        # Set table rows
        self.properties_table.setRowCount(len(properties))
        
        for row, prop in enumerate(properties):
            # Property Address
            self.properties_table.setItem(row, 0, QTableWidgetItem(prop.property_address or "Unknown"))
            
            # Mailing Address
            self.properties_table.setItem(row, 1, QTableWidgetItem(prop.mailing_address or "Unknown"))
            
            # Value
            value_str = format_currency(prop.property_value, prop) if hasattr(prop, 'property_value') else "$0"
            self.properties_table.setItem(row, 2, QTableWidgetItem(value_str))
            
            # Type
            owner_type = prop.owner_type if hasattr(prop, 'owner_type') else get_owner_type(self.owner)
            self.properties_table.setItem(row, 3, QTableWidgetItem(owner_type))
            
            # Phone Count
            phone_count = len(prop.phone_numbers) if hasattr(prop, 'phone_numbers') else 0
            self.properties_table.setItem(row, 4, QTableWidgetItem(str(phone_count)))
    
    @monitor_cpu_usage
    def populate_phones_table(self):
        """Populate phones table."""
        phones = self.owner.all_phones if hasattr(self.owner, 'all_phones') else []
        
        # Set table rows
        self.phones_table.setRowCount(len(phones))
        
        for row, phone in enumerate(phones):
            # Number
            self.phones_table.setItem(row, 0, QTableWidgetItem(phone.number))
            
            # Status
            status_item = QTableWidgetItem(phone.status)
            self._set_status_color(status_item, phone.status)
            self.phones_table.setItem(row, 1, status_item)
            
            # Type
            self.phones_table.setItem(row, 2, QTableWidgetItem(phone.phone_type))
            
            # Priority
            priority_str = f"{phone.priority_score:.2f}" if hasattr(phone, 'priority_score') else "N/A"
            self.phones_table.setItem(row, 3, QTableWidgetItem(priority_str))
            
            # Tags
            tags = phone.tags if hasattr(phone, 'tags') else ""
            self.phones_table.setItem(row, 4, QTableWidgetItem(tags))
            
            # Confidence
            confidence_str = f"{phone.confidence:.2f}" if hasattr(phone, 'confidence') else "N/A"
            self.phones_table.setItem(row, 5, QTableWidgetItem(confidence_str))
            
            # Original Column
            self.phones_table.setItem(row, 6, QTableWidgetItem(phone.original_column))
    
    def _set_status_color(self, item: QTableWidgetItem, status: str):
        """Set color based on phone status."""
        if status == "CORRECT":
            item.setBackground(QColor(200, 255, 200))  # Light green
        elif status == "WRONG":
            item.setBackground(QColor(255, 200, 200))  # Light red
        elif status == "DEAD":
            item.setBackground(QColor(255, 255, 200))  # Light yellow
        else:
            item.setBackground(QColor(240, 240, 240))  # Light gray
    
    def _get_mailing_address(self) -> str:
        """Get proper mailing address."""
        if self.owner.mailing_address and self.owner.mailing_address != "Unknown":
            return self.owner.mailing_address
        
        # Try to get from property_details
        if hasattr(self.owner, 'property_details') and self.owner.property_details:
            for prop in self.owner.property_details:
                if prop.mailing_address and prop.mailing_address != "Unknown":
                    return prop.mailing_address
        
        return "No mailing address"
    
    @monitor_cpu_usage
    def export_owner_data(self):
        """Export owner data to CSV/Excel."""
        try:
            # Create export directory
            export_dir = Path("data/exports/owner_details")
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Export properties
            properties_data = []
            if hasattr(self.owner, 'property_details') and self.owner.property_details:
                for prop in self.owner.property_details:
                    properties_data.append({
                        'Property Address': prop.property_address,
                        'Mailing Address': prop.mailing_address,
                        'Value': prop.property_value,
                        'Type': prop.owner_type
                    })
            
            # Export phones
            phones_data = []
            if hasattr(self.owner, 'all_phones'):
                for phone in self.owner.all_phones:
                    phones_data.append({
                        'Number': phone.number,
                        'Status': phone.status,
                        'Type': phone.phone_type,
                        'Priority': phone.priority_score,
                        'Tags': phone.tags,
                        'Confidence': phone.confidence,
                        'Original Column': phone.original_column
                    })
            
            # Save to Excel
            owner_name = get_owner_name(self.owner).replace('/', '_').replace('\\', '_')
            filename = f"{owner_name}_details.xlsx"
            filepath = export_dir / filename
            
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                # Owner summary
                summary_data = {
                    'Field': ['Name', 'Type', 'Mailing Address', 'Property Count', 'Total Value', 'Phone Quality', 'Confidence'],
                    'Value': [
                        get_owner_name(self.owner),
                        get_owner_type(self.owner),
                        self._get_mailing_address(),
                        self.owner.property_count,
                        self.owner.total_property_value,
                        self.owner.phone_quality_score,
                        get_confidence_level(self.owner)
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Owner Summary', index=False)
                
                # Properties
                if properties_data:
                    pd.DataFrame(properties_data).to_excel(writer, sheet_name='Properties', index=False)
                
                # Phones
                if phones_data:
                    pd.DataFrame(phones_data).to_excel(writer, sheet_name='Phone Numbers', index=False)
            
            QMessageBox.information(self, "Export Successful", 
                                  f"Owner data exported to:\n{filepath}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", 
                               f"Failed to export owner data:\n{str(e)}")
    
    def skip_trace(self):
        """Perform skip trace on this owner."""
        QMessageBox.information(self, "Skip Trace", 
                              "Skip trace functionality will be implemented in a future update.") 