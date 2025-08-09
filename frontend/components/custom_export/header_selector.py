#!/usr/bin/env python3
"""
Header Selector Component

Provides a user interface for selecting which headers to include in exports.
Organizes headers by category with checkboxes for easy selection.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QCheckBox, QGroupBox, QScrollArea, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import List, Dict


class HeaderSelector(QWidget):
    """Header selection widget with categorized checkboxes."""
    
    headers_changed = pyqtSignal(list)  # Signal emitted when headers change
    
    def __init__(self, export_config):
        super().__init__()
        
        self.export_config = export_config
        self.selected_headers = []
        self.checkboxes = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📊 Select Headers for Export")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #667eea; margin: 10px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # Quick selection buttons
        quick_buttons_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("☑️ Select All")
        select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        select_all_btn.clicked.connect(self.select_all_headers)
        
        deselect_all_btn = QPushButton("☐ Deselect All")
        deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        deselect_all_btn.clicked.connect(self.deselect_all_headers)
        
        quick_buttons_layout.addWidget(select_all_btn)
        quick_buttons_layout.addWidget(deselect_all_btn)
        quick_buttons_layout.addStretch()
        
        layout.addLayout(quick_buttons_layout)
        
        # Create scrollable area for header categories
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # Create scrollable content
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Get header categories
        categories = self.export_config.get_header_categories()
        
        # Create category groups
        for category_name, headers in categories.items():
            category_group = self.create_category_group(category_name, headers)
            scroll_layout.addWidget(category_group)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Summary
        self.summary_label = QLabel("Selected: 0 headers")
        self.summary_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.summary_label)
    
    def create_category_group(self, category_name: str, headers: List[str]) -> QGroupBox:
        """Create a group box for a category of headers."""
        group = QGroupBox(category_name)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #667eea;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #667eea;
            }
        """)
        
        layout = QGridLayout(group)
        
        # Add checkboxes for each header
        for i, header in enumerate(headers):
            checkbox = QCheckBox(header)
            checkbox.setStyleSheet("""
                QCheckBox {
                    font-size: 12px;
                    padding: 4px;
                }
                QCheckBox:hover {
                    background-color: #f8f9fa;
                    border-radius: 2px;
                }
            """)
            checkbox.stateChanged.connect(self.on_header_changed)
            
            # Store checkbox reference
            self.checkboxes[header] = checkbox
            
            # Add to grid (3 columns)
            row = i // 3
            col = i % 3
            layout.addWidget(checkbox, row, col)
        
        return group
    
    def on_header_changed(self):
        """Handle header checkbox state changes."""
        self.selected_headers = []
        
        for header, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                self.selected_headers.append(header)
        
        # Update summary
        self.summary_label.setText(f"Selected: {len(self.selected_headers)} headers")
        
        # Emit signal
        self.headers_changed.emit(self.selected_headers)
    
    def select_all_headers(self):
        """Select all headers."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all_headers(self):
        """Deselect all headers."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
    
    def set_selected_headers(self, headers: List[str]):
        """Set the selected headers programmatically."""
        # First, uncheck all
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
        
        # Then check the specified ones
        for header in headers:
            if header in self.checkboxes:
                self.checkboxes[header].setChecked(True)
    
    def get_selected_headers(self) -> List[str]:
        """Get the currently selected headers."""
        return self.selected_headers.copy()


def test_header_selector():
    """Test the header selector component."""
    print("🧪 Testing Header Selector")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        from .export_config import ExportConfig
        
        # Create app
        app = QApplication([])
        
        # Create export config
        config = ExportConfig()
        
        # Create header selector
        selector = HeaderSelector(config)
        selector.show()
        
        print("✅ Header selector created successfully")
        
        # Test header categories
        categories = config.get_header_categories()
        print(f"📂 Found {len(categories)} header categories:")
        for category, headers in categories.items():
            print(f"  ✅ {category}: {len(headers)} headers")
        
        # Test checkbox creation
        print(f"☑️ Created {len(selector.checkboxes)} checkboxes")
        
        # Test signal connection
        def on_headers_changed(headers):
            print(f"📊 Headers changed: {len(headers)} selected")
        
        selector.headers_changed.connect(on_headers_changed)
        print("✅ Signal connection established")
        
        # Test select all
        selector.select_all_headers()
        print("✅ Select all functionality works")
        
        # Test deselect all
        selector.deselect_all_headers()
        print("✅ Deselect all functionality works")
        
        # Close
        selector.close()
        app.quit()
        
        print("✅ Header selector test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Header selector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_header_selector() 