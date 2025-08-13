#!/usr/bin/env python3
"""
Efficient Table Manager

Handles large datasets with pagination, virtual scrolling, and header sorting
to reduce CPU usage and memory consumption.
"""

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from typing import List, Dict, Any, Callable, Optional
from enum import Enum
import math

from backend.utils.phone_data_utils import PhoneDataUtils, PhoneDataFormatter


class SortOrder(Enum):
    ASCENDING = Qt.AscendingOrder
    DESCENDING = Qt.DescendingOrder


class SortableHeader(QHeaderView):
    """Custom header that supports sorting with visual indicators."""
    
    sort_changed = pyqtSignal(int, SortOrder)  # column, order
    
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.sectionClicked.connect(self._on_section_clicked)
        self._sort_column = -1
        self._sort_order = SortOrder.ASCENDING
    
    def _on_section_clicked(self, logical_index):
        """Handle header click for sorting."""
        if logical_index == self._sort_column:
            # Toggle sort order
            self._sort_order = SortOrder.DESCENDING if self._sort_order == SortOrder.ASCENDING else SortOrder.ASCENDING
        else:
            # New column, start with ascending
            self._sort_column = logical_index
            self._sort_order = SortOrder.ASCENDING
        
        # Update visual indicator
        self.setSortIndicator(self._sort_column, self._sort_order.value)
        
        # Emit signal
        self.sort_changed.emit(self._sort_column, self._sort_order)


class EfficientTableManager(QObject):
    """Manages efficient table operations for large datasets."""
    
    def __init__(self, table: QTableWidget, page_size: int = 1000):
        super().__init__()
        self.table = table
        self.page_size = page_size
        self.current_page = 0
        self.total_pages = 0
        self.all_data = []
        self.filtered_data = []
        self.sort_column = 0
        self.sort_order = SortOrder.DESCENDING
        
        # Setup table
        self._setup_table()
        
        # Connect signals
        self.header = SortableHeader(Qt.Horizontal, self.table)
        self.table.setHorizontalHeader(self.header)
        self.header.sort_changed.connect(self._on_sort_changed)
    
    def _setup_table(self):
        """Setup table for efficient operation."""
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Set selection behavior
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Optimize for large datasets
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set column stretch
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
    
    def set_data(self, data: List[Any], column_configs: List[Dict[str, Any]]):
        """
        Set data with column configurations.
        
        Args:
            data: List of data objects
            column_configs: List of column configurations
                [{'name': 'Column Name', 'key': 'data_key', 'formatter': callable}]
        """
        self.all_data = data
        self.filtered_data = data.copy()
        
        # Setup columns
        self._setup_columns(column_configs)
        
        # Apply current sorting if any
        if hasattr(self, 'sort_column') and hasattr(self, 'sort_order'):
            self._sort_data()
        
        # Calculate pagination
        self.total_pages = math.ceil(len(self.filtered_data) / self.page_size)
        self.current_page = 0
        
        # Load first page
        self._load_current_page()
    
    def _setup_columns(self, column_configs: List[Dict[str, Any]]):
        """Setup table columns."""
        self.table.setColumnCount(len(column_configs))
        
        # Set headers
        headers = [config['name'] for config in column_configs]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Store column configs
        self.column_configs = column_configs
        
        # Set column widths
        for i, config in enumerate(column_configs):
            width = config.get('width', 150)
            self.table.setColumnWidth(i, width)
    
    def _load_current_page(self):
        """Load current page of data."""
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self.filtered_data[start_idx:end_idx]
        
        # Clear table
        self.table.setRowCount(len(page_data))
        
        # Populate rows
        for row, item in enumerate(page_data):
            for col, config in enumerate(self.column_configs):
                value = self._get_cell_value(item, config)
                table_item = QTableWidgetItem(str(value))
                
                # Set alignment for numeric columns
                if config.get('numeric', False):
                    table_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                self.table.setItem(row, col, table_item)
    
    def _get_cell_value(self, item: Any, config: Dict[str, Any]) -> str:
        """Get formatted cell value."""
        key = config['key']
        formatter = config.get('formatter')
        
        # Get raw value
        if callable(key):
            value = key(item)
        else:
            value = getattr(item, key, '')
        
        # Apply formatter
        if formatter:
            return formatter(value, item)
        
        return str(value) if value is not None else ''
    
    def _on_sort_changed(self, column: int, order: SortOrder):
        """Handle sort change."""
        self.sort_column = column
        self.sort_order = order
        
        # Sort data
        self._sort_data()
        
        # Reload current page
        self._load_current_page()
    
    def _sort_data(self):
        """Sort filtered data."""
        if not self.filtered_data:
            return
        
        # Get sort key function
        config = self.column_configs[self.sort_column]
        key_func = config.get('sort_key', config['key'])
        
        # Sort data
        reverse = (self.sort_order == SortOrder.DESCENDING)
        
        # Handle numeric sorting properly
        if config.get('numeric', False):
            # For numeric columns, convert to float for proper sorting
            def numeric_key(x):
                try:
                    value = key_func(x) if callable(key_func) else getattr(x, key_func, 0)
                    return float(value) if value is not None else 0.0
                except (ValueError, TypeError):
                    return 0.0
            
            # Debug: Print first few values to see what we're sorting
            print(f"🔍 Sorting numeric column '{config['name']}' (reverse={reverse})")
            print(f"   Sample values: {[numeric_key(x) for x in self.filtered_data[:5]]}")
            
            self.filtered_data.sort(key=numeric_key, reverse=reverse)
            
            # Debug: Print first few sorted values
            print(f"   After sorting: {[numeric_key(x) for x in self.filtered_data[:5]]}")
        else:
            # For non-numeric columns, use string sorting
            if callable(key_func):
                self.filtered_data.sort(key=lambda x: str(key_func(x) or ''), reverse=reverse)
            else:
                self.filtered_data.sort(key=lambda x: str(getattr(x, key_func, '') or ''), reverse=reverse)
    
    def apply_filter(self, filter_func: Callable[[Any], bool]):
        """Apply filter to data."""
        self.filtered_data = [item for item in self.all_data if filter_func(item)]
        
        # Reset pagination
        self.total_pages = math.ceil(len(self.filtered_data) / self.page_size)
        self.current_page = 0
        
        # Reload data
        self._load_current_page()
    
    def clear_filter(self):
        """Clear all filters."""
        self.filtered_data = self.all_data.copy()
        
        # Reset pagination
        self.total_pages = math.ceil(len(self.filtered_data) / self.page_size)
        self.current_page = 0
        
        # Reload data
        self._load_current_page()
    
    def next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._load_current_page()
    
    def prev_page(self):
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self._load_current_page()
    
    def go_to_page(self, page: int):
        """Go to specific page."""
        if 0 <= page < self.total_pages:
            self.current_page = page
            self._load_current_page()
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.filtered_data))
        
        return {
            'current_page': self.current_page + 1,
            'total_pages': self.total_pages,
            'start_index': start_idx + 1,
            'end_index': end_idx,
            'total_items': len(self.filtered_data),
            'has_next': self.current_page < self.total_pages - 1,
            'has_prev': self.current_page > 0
        }
    
    def get_sorted_data_preview(self, count: int = 10) -> List[Any]:
        """Get preview of sorted data for debugging."""
        if not self.filtered_data:
            return []
        
        # Get the first 'count' items from the sorted dataset
        preview = self.filtered_data[:count]
        
        # Extract key values for the current sort column
        if hasattr(self, 'sort_column') and self.sort_column < len(self.column_configs):
            config = self.column_configs[self.sort_column]
            key_func = config.get('sort_key', config['key'])
            
            if config.get('numeric', False):
                values = []
                for item in preview:
                    try:
                        value = key_func(item) if callable(key_func) else getattr(item, key_func, 0)
                        values.append(float(value) if value is not None else 0.0)
                    except (ValueError, TypeError):
                        values.append(0.0)
                return values
            else:
                values = []
                for item in preview:
                    value = key_func(item) if callable(key_func) else getattr(item, key_func, '')
                    values.append(str(value) if value is not None else '')
                return values
        
        return []


# Utility functions for common data formatting
def format_currency(value: float, item: Any = None) -> str:
    """Format value as currency."""
    if value is None or value == 0:
        return "$0"
    return f"${value:,.0f}"


def format_percentage(value: float, item: Any = None) -> str:
    """Format value as percentage."""
    if value is None:
        return "N/A"
    return f"{value:.1f}%"


def format_phone_quality_pete(item: Any) -> str:
    """Format phone quality using Pete data structure."""
    formatter = PhoneDataFormatter()
    phone_data = formatter.format_owner_phone_data(item)
    return phone_data['phone_quality']


def format_phone_count_pete(item: Any) -> str:
    """Format phone count using Pete data structure."""
    formatter = PhoneDataFormatter()
    phone_data = formatter.format_owner_phone_data(item)
    return phone_data['phone_count']


def get_owner_name(item: Any) -> str:
    """Get owner name with hierarchy."""
    if item.individual_name:
        return item.individual_name
    elif item.business_name:
        return item.business_name
    else:
        return "Unknown"


def get_owner_type(item: Any) -> str:
    """Get owner type."""
    return "LLC/Business" if item.is_business_owner else "Individual"


def get_confidence_level(item: Any) -> str:
    """Get confidence level."""
    if not item.confidence_score:
        return "Unknown"
    
    if item.confidence_score >= 0.8:
        return "High"
    elif item.confidence_score >= 0.6:
        return "Medium"
    else:
        return "Low"


def get_best_contact_method_pete(item: Any) -> str:
    """Get best contact method using Pete data structure."""
    formatter = PhoneDataFormatter()
    phone_data = formatter.format_owner_phone_data(item)
    return phone_data['best_contact'] 