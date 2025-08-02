"""
Standardized Preview UI Component

Component for previewing and downloading standardized data after mapping.
"""

import pandas as pd
from typing import Optional, Callable
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

from frontend.components.base_component import BaseComponent
from frontend.constants import DEFAULT_RULES_CONFIG

class StandardizedPreviewUI(BaseComponent):
    """
    Preview component for standardized data.
    
    Features:
    - Tabular preview of transformed data
    - Download options (CSV, XLSX)
    - Navigation controls
    """
    
    def __init__(self, parent=None, df: Optional[pd.DataFrame] = None,
                 on_back: Optional[Callable] = None, 
                 on_exit: Optional[Callable] = None):
        """
        Initialize standardized preview UI.
        
        Args:
            parent: Parent widget
            df: Standardized DataFrame to preview
            on_back: Callback for back button
            on_exit: Callback for exit button
        """
        super().__init__(parent, show_logo=True, show_navigation=True,
                         on_back=on_back, on_exit=on_exit)
        
        if df is None:
            raise ValueError("DataFrame is required for preview")
        
        self.df = df
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Title
        title_label = QLabel('Standardized Data Preview')
        title_label.setStyleSheet('font-weight: bold; font-size: 16px;')
        self.layout.addWidget(title_label)
        
        # Info label
        info_label = QLabel(f'Showing {len(self.df)} rows, {len(self.df.columns)} columns')
        info_label.setStyleSheet('color: #666; font-size: 12px;')
        self.layout.addWidget(info_label)
        
        # Preview table
        self._setup_preview_table()
        
        # Download buttons
        self._setup_download_buttons()
    
    def _setup_preview_table(self):
        """Setup the data preview table."""
        self.table_widget = QTableWidget()
        
        # Configure table size based on rules
        rules = DEFAULT_RULES_CONFIG
        preview_rows = min(rules.get('preview_row_count', 10), len(self.df))
        preview_cols = len(self.df.columns)
        
        self.table_widget.setRowCount(preview_rows)
        self.table_widget.setColumnCount(preview_cols)
        self.table_widget.setHorizontalHeaderLabels([str(col) for col in self.df.columns])
        
        # Populate table with data
        for i in range(preview_rows):
            for j in range(preview_cols):
                val = str(self.df.iloc[i, j]) if pd.notna(self.df.iloc[i, j]) else ''
                item = QTableWidgetItem(val)
                self.table_widget.setItem(i, j, item)
        
        # Configure table appearance
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.resizeColumnsToContents()
        
        self.layout.addWidget(self.table_widget)
    
    def _setup_download_buttons(self):
        """Setup download action buttons."""
        button_layout = QHBoxLayout()
        
        # Download buttons
        self.download_csv_btn = QPushButton('Download as CSV')
        self.download_xlsx_btn = QPushButton('Download as XLSX')
        
        # Style download buttons
        download_style = """
        QPushButton {
            background-color: #1976d2;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1565c0;
        }
        QPushButton:pressed {
            background-color: #0d47a1;
        }
        """
        self.download_csv_btn.setStyleSheet(download_style)
        self.download_xlsx_btn.setStyleSheet(download_style)
        
        # Connect signals
        self.download_csv_btn.clicked.connect(self.download_csv)
        self.download_xlsx_btn.clicked.connect(self.download_xlsx)
        
        button_layout.addWidget(self.download_csv_btn)
        button_layout.addWidget(self.download_xlsx_btn)
        button_layout.addStretch()  # Push buttons to the left
        
        self.layout.addLayout(button_layout)
    
    def download_csv(self):
        """Handle CSV download."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            'Save Standardized Data as CSV', 
            'standardized_data.csv',
            'CSV Files (*.csv)'
        )
        
        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                QMessageBox.information(
                    self, 
                    'Download Complete', 
                    f'Standardized data saved as CSV to:\n{file_path}'
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    'Download Error', 
                    f'Failed to save CSV file:\n{str(e)}'
                )
    
    def download_xlsx(self):
        """Handle Excel download."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            'Save Standardized Data as Excel', 
            'standardized_data.xlsx',
            'Excel Files (*.xlsx)'
        )
        
        if file_path:
            try:
                self.df.to_excel(file_path, index=False)
                QMessageBox.information(
                    self, 
                    'Download Complete', 
                    f'Standardized data saved as Excel to:\n{file_path}'
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    'Download Error', 
                    f'Failed to save Excel file:\n{str(e)}'
                )
    
    def refresh_preview(self, new_df: pd.DataFrame):
        """Refresh the preview with new data."""
        self.df = new_df
        
        # Remove existing table
        if self.table_widget:
            self.layout.removeWidget(self.table_widget)
            self.table_widget.deleteLater()
        
        # Setup new table
        self._setup_preview_table()
    
    def get_data(self) -> pd.DataFrame:
        """Get the current DataFrame."""
        return self.df.copy()