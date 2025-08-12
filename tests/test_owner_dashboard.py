#!/usr/bin/env python3
"""
Test Owner Dashboard Component

Simple test to verify the owner dashboard loads and displays data correctly.
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from frontend.components.owner_dashboard.owner_dashboard import OwnerDashboard


def test_owner_dashboard():
    """Test the owner dashboard component."""
    app = QApplication(sys.argv)
    
    # Create the owner dashboard
    dashboard = OwnerDashboard()
    dashboard.show()
    
    # Auto-load data after a short delay
    def load_data():
        dashboard.load_owner_data()
    
    timer = QTimer()
    timer.timeout.connect(load_data)
    timer.singleShot(1000, load_data)  # Load data after 1 second
    
    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_owner_dashboard() 