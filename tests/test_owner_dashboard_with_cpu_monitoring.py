#!/usr/bin/env python3
"""
Test Owner Dashboard with CPU Monitoring

Tests the improved owner dashboard with CPU usage monitoring to identify
what operations are causing high CPU usage.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add project root to path
sys.path.insert(0, '.')

from frontend.components.owner_dashboard.owner_dashboard import OwnerDashboard
from backend.utils.cpu_monitor import log_cpu_summary


def test_owner_dashboard_with_monitoring():
    """Test the improved owner dashboard with CPU monitoring."""
    app = QApplication(sys.argv)
    
    # Create owner dashboard
    dashboard = OwnerDashboard()
    dashboard.show()
    
    # Load data after a short delay
    QTimer.singleShot(2000, dashboard.load_owner_data)
    
    print("✅ Owner Dashboard loaded successfully!")
    print("📋 Features to test:")
    print("   • Click column headers to sort")
    print("   • Use filters and search")
    print("   • Click on Properties column to open details")
    print("   • Navigate through pages")
    print("   • Check that mailing addresses show properly")
    print("   • Verify properties list shows all properties")
    print("🔍 CPU monitoring is active - check logs for usage data")
    
    # Log CPU summary when app closes
    app.aboutToQuit.connect(log_cpu_summary)
    
    return app.exec_()


if __name__ == "__main__":
    test_owner_dashboard_with_monitoring() 