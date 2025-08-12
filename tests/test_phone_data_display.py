#!/usr/bin/env python3
"""
Test Phone Data Display

Tests that phone data is properly displayed with PhoneData objects,
including status, tags, and prioritization.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add project root to path
sys.path.insert(0, '.')

from frontend.components.owner_dashboard.owner_dashboard import OwnerDashboard
from backend.utils.cpu_monitor import log_cpu_summary


def test_phone_data_display():
    """Test phone data display with proper PhoneData objects."""
    app = QApplication(sys.argv)
    
    # Create owner dashboard
    dashboard = OwnerDashboard()
    dashboard.show()
    
    # Load data after a short delay
    QTimer.singleShot(2000, dashboard.load_owner_data)
    
    print("✅ Owner Dashboard loaded successfully!")
    print("📋 Phone Data Features to test:")
    print("   • Phone Count should show: correct/total (pete_prioritized)")
    print("   • Phone Quality should show: score/10 (phone_count phones)")
    print("   • Best Contact should show: method (phone_number)")
    print("   • Click Properties column to see detailed phone analysis")
    print("   • Phone status should be color-coded in details view")
    print("🔍 CPU monitoring is active - check logs for usage data")
    
    # Log CPU summary when app closes
    app.aboutToQuit.connect(log_cpu_summary)
    
    return app.exec_()


if __name__ == "__main__":
    test_phone_data_display() 