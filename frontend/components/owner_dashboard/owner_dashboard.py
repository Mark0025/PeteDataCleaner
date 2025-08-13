#!/usr/bin/env python3
"""
Owner Dashboard Component

Main dashboard component for displaying existing owner objects
with comprehensive property portfolio analysis.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QPushButton, QComboBox, QLineEdit, QFrame,
    QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from typing import List, Dict, Any, Optional
from loguru import logger

from backend.utils.owner_persistence_manager import load_property_owners_persistent
from backend.utils.efficient_table_manager import EfficientTableManager, format_currency, format_phone_quality_pete, format_phone_count_pete, get_owner_name, get_owner_type, get_confidence_level, get_best_contact_method_pete
from backend.utils.cpu_monitor import monitor_cpu_usage, start_cpu_monitoring, stop_cpu_monitoring, log_cpu_summary
from .owner_dashboard_utils import get_owner_dashboard_utils


class OwnerDashboard(QWidget):
    """Main owner dashboard component using existing owner objects."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.owner_objects = []
        self.table_manager = None
        
        # Initialize utilities
        self.utils = get_owner_dashboard_utils()
        
        self.setup_ui()
        
        # Start CPU monitoring
        start_cpu_monitoring()
        
        # Add performance optimization
        self._setup_performance_optimization()
    
    def setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🏠 Owner Dashboard - All 269K+ Owners")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #667eea; margin: 20px;")
        layout.addWidget(header)
        
        # Summary cards
        self.create_summary_cards(layout)
        
        # Filters and search
        self.create_filters(layout)
        
        # Owner table
        self.create_owner_table(layout)
        
        # Pagination controls
        self.create_pagination_controls(layout)
        
        # Action buttons
        self.create_action_buttons(layout)
    
    def create_summary_cards(self, layout):
        """Create summary statistics cards."""
        cards_layout = QHBoxLayout()
        
        # Total Owners Card
        self.total_owners_card = self.create_card("👥 Total Owners", "Loading...")
        cards_layout.addWidget(self.total_owners_card)
        
        # Total Properties Card
        self.total_properties_card = self.create_card("🏠 Total Properties", "Loading...")
        cards_layout.addWidget(self.total_properties_card)
        
        # Total Value Card
        self.total_value_card = self.create_card("💰 Total Value", "Loading...")
        cards_layout.addWidget(self.total_value_card)
        
        # High Confidence Card
        self.high_confidence_card = self.create_card("🎯 High Confidence", "Loading...")
        cards_layout.addWidget(self.high_confidence_card)
        
        layout.addLayout(cards_layout)
    
    def create_card(self, title: str, value: str) -> QFrame:
        """Create a summary card."""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #667eea;")
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setStyleSheet("color: #333;")
        card_layout.addWidget(value_label)
        
        return card
    
    def create_filters(self, layout):
        """Create filter controls."""
        filter_layout = QHBoxLayout()
        
        # Owner type filter
        filter_label = QLabel("Filter by:")
        filter_layout.addWidget(filter_label)
        
        self.owner_filter_combo = QComboBox()
        self.owner_filter_combo.addItems(["All Owners", "Business Entities", "Individual Owners", "Multi-Property", "High Confidence"])
        self.owner_filter_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.owner_filter_combo)
        
        # Search
        search_label = QLabel("Search:")
        filter_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, address, or property...")
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input)
        
        # Sort info
        sort_info = QLabel("💡 Click column headers to sort")
        sort_info.setStyleSheet("color: #666; font-style: italic;")
        filter_layout.addWidget(sort_info)
        
        layout.addLayout(filter_layout)
    
    def create_pagination_controls(self, layout):
        """Create pagination controls."""
        pagination_layout = QHBoxLayout()
        
        # Page info label
        self.page_info_label = QLabel("Page 1 of 1")
        pagination_layout.addWidget(self.page_info_label)
        
        # Navigation buttons
        self.prev_page_btn = QPushButton("← Previous")
        self.prev_page_btn.clicked.connect(self.prev_page)
        self.prev_page_btn.setEnabled(False)
        pagination_layout.addWidget(self.prev_page_btn)
        
        self.next_page_btn = QPushButton("Next →")
        self.next_page_btn.clicked.connect(self.next_page)
        self.next_page_btn.setEnabled(False)
        pagination_layout.addWidget(self.next_page_btn)
        
        # Page size selector
        page_size_label = QLabel("Page Size:")
        pagination_layout.addWidget(page_size_label)
        
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["500", "1000", "2000", "5000"])
        self.page_size_combo.setCurrentText("1000")
        self.page_size_combo.currentTextChanged.connect(self.change_page_size)
        pagination_layout.addWidget(self.page_size_combo)
        
        layout.addLayout(pagination_layout)
    
    def create_owner_table(self, layout):
        """Create the owner data table with efficient manager."""
        self.owner_table = QTableWidget()
        
        # Create efficient table manager
        self.table_manager = EfficientTableManager(self.owner_table, page_size=1000)
        
        # Ensure sorting is enabled
        self.owner_table.setSortingEnabled(True)
        
        # Setup click handlers
        self.setup_table_click_handlers()
        
        layout.addWidget(self.owner_table)
    
    def setup_table_click_handlers(self):
        """Setup click handlers for table interactions."""
        self.owner_table.cellClicked.connect(self.on_cell_clicked)
    
    def on_cell_clicked(self, row, column):
        """Handle cell clicks."""
        if column == 9:  # Properties column
            self.show_property_details(row)
    
    def show_property_details(self, row):
        """Show property details for selected owner."""
        if not self.table_manager:
            return
        
        # Get owner data for this row
        page_info = self.table_manager.get_page_info()
        start_idx = page_info['start_index'] - 1
        owner = self.owner_objects[start_idx + row]
        
        # Open property details window
        from frontend.modules.property_owner_details import PropertyOwnerDetails
        details_window = PropertyOwnerDetails(owner)
        details_window.show()
    
    def create_action_buttons(self, layout):
        """Create action buttons."""
        button_layout = QHBoxLayout()
        
        # Load Data Button
        self.load_button = QPushButton("📊 Load All Owner Data")
        self.load_button.setStyleSheet("""
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
        self.load_button.clicked.connect(self.load_owner_data)
        button_layout.addWidget(self.load_button)
        
        # Export Button
        self.export_button = QPushButton("📤 Export Data")
        self.export_button.setStyleSheet("""
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
        self.export_button.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        button_layout.addWidget(self.progress_bar)
        
        layout.addLayout(button_layout)
    
    def load_owner_data(self):
        """Load all owner data from persistence manager."""
        self.load_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Run in background thread
        self.load_thread = LoadOwnerDataThread()
        self.load_thread.data_loaded.connect(self.on_data_loaded)
        self.load_thread.error_occurred.connect(self.on_load_error)
        self.load_thread.start()
    
    def on_data_loaded(self, owner_objects: List[Any], stats: Dict[str, Any]):
        """Handle loaded owner data."""
        self.owner_objects = owner_objects
        
        # Update summary cards
        self.update_summary_cards(stats)
        
        # Populate table
        self.populate_owner_table(owner_objects)
        
        # Reset UI
        self.load_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        QMessageBox.information(self, "Success", f"Loaded {len(owner_objects):,} owner objects successfully!")
    
    def on_load_error(self, error_message: str):
        """Handle load error."""
        self.load_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Failed to load owner data: {error_message}")
    
    def update_summary_cards(self, stats: Dict[str, Any]):
        """Update summary cards with statistics."""
        # Find the value labels in the cards
        total_owners_label = self.total_owners_card.findChildren(QLabel)[1]
        total_properties_label = self.total_properties_card.findChildren(QLabel)[1]
        total_value_label = self.total_value_card.findChildren(QLabel)[1]
        high_confidence_label = self.high_confidence_card.findChildren(QLabel)[1]
        
        total_owners_label.setText(f"{stats['total_owners']:,}")
        total_properties_label.setText(f"{stats['total_properties']:,}")
        total_value_label.setText(f"${stats['total_value']:,.0f}")
        high_confidence_label.setText(f"{stats['high_confidence_targets']:,}")
    
    def populate_owner_table(self, owner_objects: List[Any]):
        """Populate the owner table using efficient manager."""
        if not self.table_manager:
            return
        
        # Set data with column configurations
        self.table_manager.set_data(owner_objects, self.get_column_configs())
        
        # Update pagination controls
        self.update_pagination_controls()
    
    def prev_page(self):
        """Go to previous page."""
        if self.table_manager:
            self.table_manager.prev_page()
            self.update_pagination_controls()
    
    def next_page(self):
        """Go to next page."""
        if self.table_manager:
            self.table_manager.next_page()
            self.update_pagination_controls()
    
    def change_page_size(self):
        """Change page size."""
        if self.table_manager and self.owner_objects:
            new_size = int(self.page_size_combo.currentText())
            self.table_manager.page_size = new_size
            self.table_manager.set_data(self.owner_objects, self.get_column_configs())
            self.update_pagination_controls()
    
    def update_pagination_controls(self):
        """Update pagination controls."""
        if not self.table_manager:
            return
        
        page_info = self.table_manager.get_page_info()
        
        # Update page info
        self.page_info_label.setText(
            f"Page {page_info['current_page']} of {page_info['total_pages']} "
            f"({page_info['start_index']}-{page_info['end_index']} of {page_info['total_items']:,})"
        )
        
        # Update navigation buttons
        self.prev_page_btn.setEnabled(page_info['has_prev'])
        self.next_page_btn.setEnabled(page_info['has_next'])
    
    def get_column_configs(self):
        """Get column configurations for the table."""
        return [
            {
                'name': 'Owner Name',
                'key': get_owner_name,
                'width': 200,
                'sort_key': lambda x: get_owner_name(x).lower()
            },
            {
                'name': 'Mailing Address',
                'key': lambda x: self._get_mailing_address(x),
                'width': 250,
                'sort_key': lambda x: self._get_mailing_address(x).lower()
            },
            {
                'name': 'Property Count',
                'key': 'property_count',
                'width': 100,
                'numeric': True,
                'sort_key': 'property_count'
            },
            {
                'name': 'Total Value',
                'key': 'total_property_value',
                'formatter': format_currency,
                'width': 120,
                'numeric': True,
                'sort_key': 'total_property_value'
            },
            {
                'name': 'Phone Quality',
                'key': lambda x: format_phone_quality_pete(x),
                'width': 100,
                'numeric': False,
                'sort_key': lambda x: format_phone_quality_pete(x)
            },
            {
                'name': 'Phone Count',
                'key': lambda x: format_phone_count_pete(x),
                'width': 100,
                'numeric': False,
                'sort_key': lambda x: format_phone_count_pete(x)
            },
            {
                'name': 'Best Contact',
                'key': lambda x: get_best_contact_method_pete(x),
                'width': 150,
                'sort_key': lambda x: get_best_contact_method_pete(x).lower()
            },
            {
                'name': 'Owner Type',
                'key': get_owner_type,
                'width': 100,
                'sort_key': get_owner_type
            },
            {
                'name': 'Confidence',
                'key': get_confidence_level,
                'width': 100,
                'sort_key': 'confidence_score'
            },
            {
                'name': 'Properties',
                'key': lambda x: self._format_properties_list(x),
                'width': 300,
                'clickable': True
            }
        ]
    
    def _get_mailing_address(self, owner):
        """Get proper mailing address."""
        if owner.mailing_address and owner.mailing_address != "Unknown":
            return owner.mailing_address
        
        # Try to get from property_details
        if hasattr(owner, 'property_details') and owner.property_details:
            for prop in owner.property_details:
                if prop.mailing_address and prop.mailing_address != "Unknown":
                    return prop.mailing_address
        
        return "No mailing address"
    
    def _format_properties_list(self, owner):
        """Format properties list for display."""
        if hasattr(owner, 'property_details') and owner.property_details:
            # Use property_details for rich data
            addresses = [prop.property_address for prop in owner.property_details if prop.property_address]
        elif hasattr(owner, 'property_addresses') and owner.property_addresses:
            # Fallback to property_addresses
            addresses = owner.property_addresses
        else:
            addresses = [owner.property_address] if owner.property_address else []
        
        if not addresses:
            return "No properties"
        
        # Show first 3 + count
        if len(addresses) <= 3:
            return ", ".join(addresses)
        else:
            return ", ".join(addresses[:3]) + f" (+{len(addresses) - 3} more)"
    
    def apply_filters(self):
        """Apply current filters to the table."""
        if not self.table_manager or not self.owner_objects:
            return
        
        # Get filter values
        owner_type_filter = self.owner_filter_combo.currentText()
        search_term = self.search_input.text()
        
        # Create filters dictionary
        filters = {
            'owner_type': owner_type_filter,
            'search_term': search_term
        }
        
        # Use utility to apply filters
        self.filtered_owners = self.utils['filter'].apply_filters(self.owner_objects, filters)
        
        # Update table with filtered data
        self.table_manager.set_data(self.filtered_owners, self.get_column_configs())
        
        # Update pagination controls
        self.update_pagination_controls()
        
        # Update summary cards with filtered data
        if hasattr(self, 'filtered_owners') and self.filtered_owners:
            stats = self.utils['analyzer'].analyze_owners(self.filtered_owners)
            self.update_summary_cards(stats)
    
    def export_data(self):
        """Export the current filtered data."""
        if not self.owner_objects:
            QMessageBox.warning(self, "Export", "No data to export!")
            return
        
        # Get current filtered data
        current_data = self.owner_objects
        if hasattr(self, 'filtered_owners') and self.filtered_owners:
            current_data = self.filtered_owners
        
        # Show export format selection
        from PyQt5.QtWidgets import QInputDialog
        format_type, ok = QInputDialog.getItem(
            self, "Export Format", "Select export format:",
            ["csv", "xlsx", "json"], 0, False
        )
        
        if ok and format_type:
            # Use utility to export
            success = self.utils['exporter'].export_data(
                current_data, format_type, self.get_column_configs(), self
            )
            
            if success:
                logger.info(f"Exported {len(current_data):,} owners to {format_type}")
    
    def _setup_performance_optimization(self):
        """Setup performance optimizations to reduce CPU usage."""
        # Set up periodic cache clearing
        from PyQt5.QtCore import QTimer
        
        # Clear caches every 5 minutes to prevent memory buildup
        self.cache_clear_timer = QTimer()
        self.cache_clear_timer.timeout.connect(self._clear_all_caches)
        self.cache_clear_timer.start(300000)  # 5 minutes
        
        logger.info("Performance optimization setup complete")
    
    def _clear_all_caches(self):
        """Clear all utility caches to free memory."""
        self.utils['sorter'].clear_cache()
        self.utils['filter'].clear_cache()
        self.utils['analyzer'].clear_cache()
        logger.debug("All utility caches cleared")
    
    def test_sorting(self):
        """Test sorting functionality for debugging."""
        if not self.table_manager or not self.owner_objects:
            print("❌ No table manager or owner objects to test sorting")
            return False
        
        try:
            print("🧪 Testing sorting functionality...")
            
            # Test sorting by first column (Owner Name)
            print("   Testing sort by Owner Name...")
            self.table_manager._on_sort_changed(0, 0)  # Column 0, ascending
            
            # Test sorting by third column (Property Count)
            print("   Testing sort by Property Count...")
            self.table_manager._on_sort_changed(2, 1)  # Column 2, descending
            
            print("✅ Sorting tests completed")
            return True
            
        except Exception as e:
            print(f"❌ Sorting test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


class LoadOwnerDataThread(QThread):
    """Background thread for loading owner data."""
    
    data_loaded = pyqtSignal(list, dict)  # owner_objects, stats
    error_occurred = pyqtSignal(str)
    
    def run(self):
        """Load owner data in background thread."""
        try:
            # Load existing owner objects from persistence manager
            owner_objects, enhanced_df = load_property_owners_persistent()
            
            if not owner_objects:
                self.error_occurred.emit("No owner objects found")
                return
            
            # Calculate summary stats
            stats = self.calculate_stats(owner_objects)
            
            # Emit results
            self.data_loaded.emit(owner_objects, stats)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def calculate_stats(self, owner_objects: List[Any]) -> Dict[str, Any]:
        """Calculate summary statistics from owner objects."""
        total_owners = len(owner_objects)
        total_properties = sum(o.property_count for o in owner_objects)
        total_value = sum(o.total_property_value for o in owner_objects)
        business_owners = sum(1 for o in owner_objects if o.is_business_owner)
        individual_owners = total_owners - business_owners
        multi_property_owners = sum(1 for o in owner_objects if o.property_count > 1)
        high_confidence_targets = sum(1 for o in owner_objects if o.confidence_score >= 0.8)
        
        return {
            'total_owners': total_owners,
            'total_properties': total_properties,
            'total_value': total_value,
            'business_owners': business_owners,
            'individual_owners': individual_owners,
            'multi_property_owners': multi_property_owners,
            'high_confidence_targets': high_confidence_targets
        } 