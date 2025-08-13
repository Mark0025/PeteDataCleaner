#!/usr/bin/env python3
"""
Test the decorator fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from frontend.components.owner_dashboard.owner_dashboard import OwnerDashboard
import inspect

def test_decorator_fix():
    """Test that the decorator fix works correctly."""
    app = QApplication([])
    
    try:
        print("🧪 Testing decorator fix...")
        
        dashboard = OwnerDashboard()
        
        # Check the method signature
        sig = inspect.signature(dashboard.load_owner_data)
        print(f"✅ Method signature: {sig}")
        
        # Check if it takes only self
        if str(sig) == '()':
            print("✅ Method signature preserved correctly!")
            
            # Now test if we can call it without errors
            try:
                # This should not crash
                dashboard.load_owner_data()
                print("✅ Method call successful - no crash!")
                return True
            except Exception as e:
                print(f"❌ Method call failed: {e}")
                return False
        else:
            print(f"❌ Method signature incorrect: {sig}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        app.quit()

if __name__ == "__main__":
    success = test_decorator_fix()
    if success:
        print("🎉 Decorator fix successful!")
    else:
        print("💥 Decorator still broken!")
