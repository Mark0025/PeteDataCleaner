"""
File Selector Component

Component for selecting and previewing data files from the upload directory.
"""

import os
import shutil
import pandas as pd
from typing import Optional, Callable
from loguru import logger

from PyQt5.QtWidgets import (
    QLabel, QComboBox, QPushButton, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt

from frontend.components.base_component import BaseComponent
from frontend.constants import UPLOAD_DIR, DEFAULT_RULES_CONFIG
from backend.utils.data_standardizer import DataStandardizer
from backend.sheets_client import SheetsClient

class FileSelector(BaseComponent):
    """
    File selection component with preview functionality.
    
    Allows users to:
    - Select files from upload directory
    - Upload new CSV files
    - Preview file contents
    - Initiate mapping to Pete headers
    """
    
    def __init__(self, parent=None, on_mapping_request: Optional[Callable] = None, 
                 on_back: Optional[Callable] = None, on_exit: Optional[Callable] = None):
        """
        Initialize file selector.
        
        Args:
            parent: Parent widget
            on_mapping_request: Callback when user requests mapping (df, pete_headers)
            on_back: Callback for back button
            on_exit: Callback for exit button
        """
        super().__init__(parent, show_logo=True, show_navigation=True, 
                         on_back=on_back, on_exit=on_exit)
        
        self.on_mapping_request = on_mapping_request
        self.selected_file: Optional[str] = None
        self.df: Optional[pd.DataFrame] = None
        self.table_widget: Optional[QTableWidget] = None
        
        self._setup_ui()
        self.refresh_file_list()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Instructions
        instructions = QLabel('Select a data file from upload/ or upload a new CSV:')
        self.layout.addWidget(instructions)
        
        # File selection
        self.file_combo = QComboBox()
        self.file_combo.currentIndexChanged.connect(self.on_file_selected)
        self.layout.addWidget(self.file_combo)
        
        # Upload and refresh buttons
        button_layout = QHBoxLayout()
        self.upload_btn = QPushButton('Upload New CSV')
        self.refresh_btn = QPushButton('Refresh List')
        self.upload_btn.clicked.connect(self.upload_new_csv)
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel('')
        self.layout.addWidget(self.status_label)
        
        # Action buttons
        self.preview_btn = QPushButton('Preview Table')
        self.preview_btn.setEnabled(False)
        self.preview_btn.clicked.connect(self.preview_table)
        self.layout.addWidget(self.preview_btn)
        
        self.map_btn = QPushButton('Map to Pete Headers')
        self.map_btn.setEnabled(False)
        self.map_btn.clicked.connect(self.map_to_pete_headers)
        self.layout.addWidget(self.map_btn)
    
    def refresh_file_list(self):
        """Refresh the list of available files."""
        try:
            files = [
                f for f in os.listdir(UPLOAD_DIR) 
                if f.lower().endswith(('.csv', '.xlsx', '.xls'))
            ]
            self.file_combo.clear()
            self.file_combo.addItems([''] + files)
            self.status_label.setText('File list refreshed.')
            logger.info('File list refreshed.')
            
            # Reset state
            self.preview_btn.setEnabled(False)
            self.map_btn.setEnabled(False)
            self.selected_file = None
            
        except Exception as e:
            logger.error(f"Failed to refresh file list: {e}")
            self.status_label.setText(f"Error refreshing files: {e}")
    
    def on_file_selected(self, idx: int):
        """Handle file selection from combo box."""
        if idx > 0:
            self.selected_file = self.file_combo.currentText()
            self.status_label.setText(f'Selected: {self.selected_file}')
            logger.info(f'Selected file: {self.selected_file}')
            self.preview_btn.setEnabled(True)
            self.map_btn.setEnabled(False)
        else:
            self.selected_file = None
            self.preview_btn.setEnabled(False)
            self.map_btn.setEnabled(False)
    
    def upload_new_csv(self):
        """Handle uploading a new CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            'Select CSV file to upload', 
            '', 
            'CSV Files (*.csv);;Excel Files (*.xlsx *.xls)'
        )
        
        if file_path:
            try:
                # Ensure upload directory exists
                os.makedirs(UPLOAD_DIR, exist_ok=True)
                
                dest_path = os.path.join(UPLOAD_DIR, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)
                
                logger.success(f"Uploaded new file: {file_path} -> {dest_path}")
                self.status_label.setText(f"Uploaded: {os.path.basename(file_path)}")
                self.refresh_file_list()
                
                # Auto-select the uploaded file
                self.file_combo.setCurrentText(os.path.basename(file_path))
                
            except Exception as e:
                logger.error(f"Failed to upload file: {e}")
                self.status_label.setText(f"Upload error: {e}")
                QMessageBox.critical(self, 'Upload Error', f'Failed to upload file: {e}')
    
    def preview_table(self):
        """Preview the selected file contents."""
        if not self.selected_file:
            QMessageBox.warning(self, 'No file selected', 'Please select a file to preview.')
            return
        
        file_path = os.path.join(UPLOAD_DIR, self.selected_file)
        
        try:
            # Load the file based on extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                df = pd.read_csv(file_path, low_memory=False)
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
            else:
                QMessageBox.warning(self, 'Unsupported file', f'Unsupported file type: {ext}')
                return
            
            self.df = df
            self._display_preview(df)
            self.map_btn.setEnabled(True)
            
            logger.info(f'Previewed file: {self.selected_file} ({len(df)} rows, {len(df.columns)} columns)')
            
        except Exception as e:
            logger.error(f'Error reading file: {e}')
            QMessageBox.critical(self, 'Error', f'Error reading file: {e}')
    
    def _display_preview(self, df: pd.DataFrame):
        """Display file preview in table widget."""
        # Remove existing table if present
        if self.table_widget:
            self.layout.removeWidget(self.table_widget)
            self.table_widget.deleteLater()
        
        # Create new table
        self.table_widget = QTableWidget()
        
        # Configure table size
        rules = DEFAULT_RULES_CONFIG
        preview_rows = min(rules.get('preview_row_count', 10), len(df))
        preview_cols = len(df.columns)
        
        self.table_widget.setRowCount(preview_rows)
        self.table_widget.setColumnCount(preview_cols)
        self.table_widget.setHorizontalHeaderLabels([str(col) for col in df.columns])
        
        # Populate table
        for i in range(preview_rows):
            for j in range(preview_cols):
                val = str(df.iloc[i, j]) if pd.notna(df.iloc[i, j]) else ''
                item = QTableWidgetItem(val)
                self.table_widget.setItem(i, j, item)
        
        # Configure table appearance
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.resizeColumnsToContents()
        
        self.layout.addWidget(self.table_widget)
        self.status_label.setText(f'Previewing: {self.selected_file} ({len(df)} rows, {len(df.columns)} cols)')
    
    def map_to_pete_headers(self):
        """Initiate mapping to Pete headers."""
        if self.df is None:
            QMessageBox.warning(self, 'No data', 'Please preview a file first.')
            return
        
        try:
            # Get Pete headers from backend
            pete_headers = self._fetch_pete_headers()
            if not pete_headers:
                raise ValueError('No Pete headers found in template sheet.')
            
            # Trigger mapping callback
            if self.on_mapping_request:
                self.on_mapping_request(self.df, pete_headers)
            
        except Exception as e:
            logger.error(f"Failed to fetch Pete headers: {e}")
            QMessageBox.critical(self, 'Error', f'Failed to fetch Pete headers: {e}')
    
    def _fetch_pete_headers(self) -> list:
        """Fetch Pete headers from the configured sheet."""
        # Use environment variables or defaults
        default_sheet_id = '11M1wYpVdfQfZOM3y5GSVj75FuYCQ0qVtOt4MbUpbZzw'
        default_tab_name = 'Sheet1'
        
        sheet_id = os.getenv('PETE_ADDRESS_TEMPLATE_SHEET_ID', default_sheet_id)
        tab_name = os.getenv('PETE_ADDRESS_TEMPLATE_SHEET_NAME', default_tab_name).replace('"', '')
        
        return DataStandardizer.load_pete_headers_from_sheet(sheet_id, tab_name)