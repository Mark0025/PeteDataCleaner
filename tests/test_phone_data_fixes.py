#!/usr/bin/env python3
"""
Test Phone Data Fixes

Tests the fixed phone data display and sorting functionality.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add project root to path
sys.path.insert(0, '.')

from frontend.components.owner_dashboard.owner_dashboard import OwnerDashboard
from backend.utils.cpu_monitor import log_cpu_summary


def test_phone_data_fixes():
    """Test the fixed phone data display and sorting."""
    app = QApplication(sys.argv)
    
    # Create owner dashboard
    dashboard = OwnerDashboard()
    dashboard.show()
    
    # Load data after a short delay
    QTimer.singleShot(2000, dashboard.load_owner_data)
    
    print("✅ Owner Dashboard loaded successfully!")
    print("📋 Phone Data Fixes to test:")
    print("   • Sorting should work without errors")
    print("   • Phone count should show actual values (not 0/0)")
    print("   • Phone quality should show scores")
    print("   • Best contact should show method with phone number")
    print("   • Click column headers to test sorting")
    print("   • Use filters and search")
    print("🔍 CPU monitoring is active - check logs for usage data")
    
    # Log CPU summary when app closes
    app.aboutToQuit.connect(log_cpu_summary)
    
    return app.exec_()


if __name__ == "__main__":
    test_phone_data_fixes() 