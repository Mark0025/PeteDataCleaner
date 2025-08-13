#!/usr/bin/env python3
"""
Test script to verify numeric sorting fix for Property Count column.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.utils.efficient_table_manager import EfficientTableManager
from PyQt5.QtWidgets import QApplication, QTableWidget
from PyQt5.QtCore import Qt

# Mock data class for testing
class MockOwner:
    def __init__(self, name, property_count, total_value):
        self.name = name
        self.property_count = property_count
        self.total_property_value = total_value

def test_numeric_sorting():
    """Test that numeric sorting works correctly."""
    print("🧪 Testing numeric sorting fix...")
    
    # Create test data with mixed property counts
    test_data = [
        MockOwner("Owner A", 8, 100000),
        MockOwner("Owner B", 52, 500000),
        MockOwner("Owner C", 5, 75000),
        MockOwner("Owner D", 7, 120000),
        MockOwner("Owner E", 6, 90000),
        MockOwner("Owner F", 8, 110000),
        MockOwner("Owner G", 7, 130000),
        MockOwner("Owner H", 6, 85000),
        MockOwner("Owner I", 6, 95000),
        MockOwner("Owner J", 5, 80000),
    ]
    
    print(f"📊 Original order: {[f'{o.name}({o.property_count})' for o in test_data]}")
    
    # Test Property Count column sorting (column 1, descending)
    column_configs = [
        {'name': 'Owner Name', 'key': 'name', 'numeric': False},
        {'name': 'Property Count', 'key': 'property_count', 'numeric': True, 'sort_key': 'property_count'},
        {'name': 'Total Value', 'key': 'total_property_value', 'numeric': True, 'sort_key': 'total_property_value'},
    ]
    
    # Create table and manager
    app = QApplication([])
    table = QTableWidget()
    manager = EfficientTableManager(table, page_size=1000)
    
    # Set data
    manager.set_data(test_data, column_configs)
    
    # Test sorting by Property Count (descending)
    print("\n🔍 Testing Property Count descending sort...")
    manager._on_sort_changed(1, manager.header._sort_order.__class__.DESCENDING)
    
    # Get sorted data
    sorted_data = manager.filtered_data
    print(f"📊 After Property Count descending sort: {[f'{o.name}({o.property_count})' for o in sorted_data]}")
    
    # Verify sorting is correct
    property_counts = [o.property_count for o in sorted_data]
    expected_descending = [52, 8, 8, 7, 7, 6, 6, 6, 5, 5]
    
    if property_counts == expected_descending:
        print("✅ Property Count descending sort is CORRECT!")
    else:
        print("❌ Property Count descending sort is WRONG!")
        print(f"   Expected: {expected_descending}")
        print(f"   Got:      {property_counts}")
    
    # Test sorting by Property Count (ascending)
    print("\n🔍 Testing Property Count ascending sort...")
    manager._on_sort_changed(1, manager.header._sort_order.__class__.ASCENDING)
    
    # Get sorted data
    sorted_data = manager.filtered_data
    print(f"📊 After Property Count ascending sort: {[f'{o.name}({o.property_count})' for o in sorted_data]}")
    
    # Verify sorting is correct
    property_counts = [o.property_count for o in sorted_data]
    expected_ascending = [5, 5, 6, 6, 6, 7, 7, 8, 8, 52]
    
    if property_counts == expected_ascending:
        print("✅ Property Count ascending sort is CORRECT!")
    else:
        print("❌ Property Count ascending sort is WRONG!")
        print(f"   Expected: {expected_ascending}")
        print(f"   Got:      {property_counts}")
    
    print("\n🎯 Sorting test completed!")
    return True

if __name__ == "__main__":
    test_numeric_sorting()
