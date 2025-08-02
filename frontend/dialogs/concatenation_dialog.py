"""
Concatenation Dialog

Dialog for creating column concatenations by selecting multiple source columns
and mapping them to a single Pete header with a configurable separator.
"""

from typing import List, Optional, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QDialogButtonBox, QMessageBox
)

class ConcatenationDialog(QDialog):
    """
    Dialog for creating column concatenations.
    
    Allows users to:
    - Select multiple source columns to concatenate
    - Choose a separator character/string
    - Map the result to a Pete header
    """
    
    def __init__(self, upload_columns: List[str], pete_headers: List[str], 
                 pre_selected_columns: Optional[List[str]] = None, parent=None):
        """
        Initialize concatenation dialog.
        
        Args:
            upload_columns: List of available upload columns
            pete_headers: List of available Pete headers  
            pre_selected_columns: Columns to pre-select for concatenation
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle('Concatenate Columns')
        
        self.upload_columns = upload_columns
        self.pete_headers = pete_headers
        self.result: Optional[Dict[str, Any]] = None
        
        self._setup_ui(pre_selected_columns)
    
    def _setup_ui(self, pre_selected_columns: Optional[List[str]]):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Source Columns Selection
        self._setup_source_selection(layout, pre_selected_columns)
        
        # Separator Input
        self._setup_separator_input(layout)
        
        # Destination Selection
        self._setup_destination_selection(layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _setup_source_selection(self, layout: QVBoxLayout, 
                              pre_selected_columns: Optional[List[str]]):
        """Setup source column selection."""
        source_layout = QHBoxLayout()
        
        self.source_cols = QListWidget()
        self.source_cols.setSelectionMode(QListWidget.MultiSelection)
        
        # Populate source columns
        for col in self.upload_columns:
            item = QListWidgetItem(col)
            self.source_cols.addItem(item)
            
            # Pre-select columns if provided
            if pre_selected_columns and col in pre_selected_columns:
                item.setSelected(True)
        
        source_layout.addWidget(QLabel('Select Columns to Concatenate:'))
        source_layout.addWidget(self.source_cols)
        layout.addLayout(source_layout)
    
    def _setup_separator_input(self, layout: QVBoxLayout):
        """Setup separator input field."""
        separator_layout = QHBoxLayout()
        separator_layout.addWidget(QLabel('Separator:'))
        
        self.separator_input = QLineEdit(' ')  # Default space separator
        self.separator_input.setToolTip('Character(s) to use between concatenated values')
        separator_layout.addWidget(self.separator_input)
        
        layout.addLayout(separator_layout)
    
    def _setup_destination_selection(self, layout: QVBoxLayout):
        """Setup destination Pete header selection."""
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel('Map to Pete Header:'))
        
        self.dest_combo = QComboBox()
        self.dest_combo.addItems([''] + self.pete_headers)
        self.dest_combo.setToolTip('Choose which Pete header will receive the concatenated data')
        dest_layout.addWidget(self.dest_combo)
        
        layout.addLayout(dest_layout)
    
    def validate_and_accept(self):
        """Validate inputs and prepare result."""
        selected_cols = [
            item.text() for item in self.source_cols.selectedItems()
        ]
        separator = self.separator_input.text()
        dest_header = self.dest_combo.currentText()
        
        # Validate inputs
        if len(selected_cols) < 2:
            QMessageBox.warning(
                self, 
                'Invalid Input', 
                'Please select at least two columns to concatenate.'
            )
            return
        
        if not dest_header:
            QMessageBox.warning(
                self, 
                'Invalid Input', 
                'Please select a destination Pete header.'
            )
            return
        
        # Prepare result
        self.result = {
            'source_columns': selected_cols,
            'separator': separator,
            'destination_header': dest_header
        }
        
        self.accept()
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the concatenation result after dialog completion."""
        return self.result