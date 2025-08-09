#!/usr/bin/env python3
"""
Export Preview Component

Provides a preview of the data that will be exported based on selected headers.
Shows a sample of the data in a table format.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTextEdit, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Optional
import pandas as pd


class ExportPreview(QWidget):
    """Export preview widget showing sample data."""
    
    def __init__(self):
        super().__init__()
        
        self.data = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("👁️ Export Preview")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #667eea; margin: 10px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)
        
        # Info label
        self.info_label = QLabel("No data available for preview. Select headers and refresh to see preview.")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-style: italic;
                padding: 20px;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Table widget
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)
        
        # Summary
        self.summary_label = QLabel("")
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
    
    def set_data(self, data: pd.DataFrame):
        """Set the data to preview."""
        self.data = data
        
        if data is None or data.empty:
            self.show_no_data()
            return
        
        self.show_data_preview(data)
    
    def show_no_data(self):
        """Show no data message."""
        self.info_label.setText("No data available for preview. Select headers and refresh to see preview.")
        self.info_label.setVisible(True)
        self.table.setVisible(False)
        self.summary_label.setText("")
    
    def show_data_preview(self, data: pd.DataFrame):
        """Show data preview in table."""
        self.info_label.setVisible(False)
        self.table.setVisible(True)
        
        # Limit to first 10 rows for preview
        preview_data = data.head(10)
        
        # Set up table
        self.table.setRowCount(len(preview_data))
        self.table.setColumnCount(len(preview_data.columns))
        
        # Set headers
        self.table.setHorizontalHeaderLabels(preview_data.columns)
        
        # Populate data
        for row_idx, (_, row) in enumerate(preview_data.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value) if pd.notna(value) else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.table.setItem(row_idx, col_idx, item)
        
        # Auto-resize columns
        self.table.resizeColumnsToContents()
        
        # Update summary
        total_rows = len(data)
        preview_rows = len(preview_data)
        total_cols = len(data.columns)
        
        summary_text = f"Preview showing {preview_rows} of {total_rows:,} rows ({total_cols} columns)"
        if total_rows > preview_rows:
            summary_text += f" - Showing first {preview_rows} rows only"
        
        self.summary_label.setText(summary_text)
    
    def clear_preview(self):
        """Clear the preview."""
        self.data = None
        self.show_no_data()


def test_export_preview():
    """Test the export preview component."""
    print("🧪 Testing Export Preview")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        import pandas as pd
        
        # Create app
        app = QApplication([])
        
        # Create sample data
        sample_data = pd.DataFrame({
            'Property Address': ['123 Main St', '456 Oak Ave', '789 Pine St'],
            'Owner Name': ['John Doe', 'Jane Smith', 'ABC Properties LLC'],
            'Phone 1': ['555-1234', '555-5678', '555-9999'],
            'Phone Status 1': ['CORRECT', 'UNKNOWN', 'WRONG'],
            'Phone Quality Score': [8.5, 6.2, 3.1]
        })
        
        # Create export preview
        preview = ExportPreview()
        preview.show()
        
        print("✅ Export preview created successfully")
        
        # Test with data
        preview.set_data(sample_data)
        print("✅ Data preview set successfully")
        
        # Test without data
        preview.clear_preview()
        print("✅ Clear preview works")
        
        # Test with data again
        preview.set_data(sample_data)
        print("✅ Data preview restored")
        
        # Close
        preview.close()
        app.quit()
        
        print("✅ Export preview test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Export preview test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_export_preview() 