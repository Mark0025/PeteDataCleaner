"""
Duplicate Removal Dialog

Interactive dialog for configuring duplicate row removal with various parameters.
"""

from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QCheckBox, QGroupBox, QListWidget, QListWidgetItem,
    QDialogButtonBox, QRadioButton, QButtonGroup, QTextEdit
)
from PyQt5.QtCore import Qt


class DuplicateRemovalDialog(QDialog):
    """
    Dialog for configuring duplicate removal parameters.
    
    Parameters:
    - Method: All columns, Selected columns, Case-insensitive
    - Keep: first, last, or False (remove all)
    - Columns: Which columns to consider for duplicates
    """
    
    def __init__(self, available_columns: List[str], parent=None):
        super().__init__(parent)
        self.available_columns = available_columns
        self.config = None
        
        self.setWindowTitle('Remove Duplicate Rows')
        self.setModal(True)
        self.resize(500, 600)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title = QLabel('🧹 Remove Duplicate Rows')
        title.setStyleSheet('font-size: 16px; font-weight: bold; color: #1976d2; margin-bottom: 10px;')
        layout.addWidget(title)
        
        desc = QLabel(
            'Configure how to identify and remove duplicate rows. '
            'Duplicates are rows that have identical values in the specified columns.'
        )
        desc.setWordWrap(True)
        desc.setStyleSheet('color: #666; margin-bottom: 15px;')
        layout.addWidget(desc)
        
        # Method selection
        method_group = QGroupBox('Duplicate Detection Method')
        method_layout = QVBoxLayout(method_group)
        
        self.method_group = QButtonGroup()
        
        self.all_columns_radio = QRadioButton('All Columns')
        self.all_columns_radio.setToolTip('Consider all columns when detecting duplicates')
        self.all_columns_radio.setChecked(True)
        self.method_group.addButton(self.all_columns_radio, 0)
        method_layout.addWidget(self.all_columns_radio)
        
        self.selected_columns_radio = QRadioButton('Selected Columns Only')
        self.selected_columns_radio.setToolTip('Only consider specific columns for duplicates')
        self.method_group.addButton(self.selected_columns_radio, 1)
        method_layout.addWidget(self.selected_columns_radio)
        
        self.ignore_case_radio = QRadioButton('Case-Insensitive (Text Columns)')
        self.ignore_case_radio.setToolTip('Ignore case differences in text columns')
        self.method_group.addButton(self.ignore_case_radio, 2)
        method_layout.addWidget(self.ignore_case_radio)
        
        self.address_based_radio = QRadioButton('Address-Based Grouping (NEW)')
        self.address_based_radio.setToolTip('Group by Property Address and create Seller 1-5 from duplicates')
        self.method_group.addButton(self.address_based_radio, 3)
        method_layout.addWidget(self.address_based_radio)
        
        self.smart_seller_radio = QRadioButton('Smart Seller Creation (NEW)')
        self.smart_seller_radio.setToolTip('Create Seller 1-5 with phone prioritization for address duplicates')
        self.method_group.addButton(self.smart_seller_radio, 4)
        method_layout.addWidget(self.smart_seller_radio)
        
        # Connect radio button changes
        self.method_group.buttonClicked.connect(self._on_method_changed)
        
        layout.addWidget(method_group)
        
        # Column selection (initially disabled)
        self.column_group = QGroupBox('Select Columns for Duplicate Detection')
        column_layout = QVBoxLayout(self.column_group)
        
        column_desc = QLabel('Select which columns to consider when identifying duplicates:')
        column_desc.setStyleSheet('color: #666; margin-bottom: 5px;')
        column_layout.addWidget(column_desc)
        
        self.column_list = QListWidget()
        self.column_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Populate column list
        for col in self.available_columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.column_list.addItem(item)
        
        column_layout.addWidget(self.column_list)
        
        # Initially disable column selection
        self.column_group.setEnabled(False)
        
        layout.addWidget(self.column_group)
        
        # Keep option
        keep_group = QGroupBox('Which Duplicates to Keep')
        keep_layout = QVBoxLayout(keep_group)
        
        self.keep_combo = QComboBox()
        self.keep_combo.addItems([
            'first - Keep first occurrence',
            'last - Keep last occurrence', 
            'False - Remove all duplicates (keep none)'
        ])
        self.keep_combo.setCurrentIndex(0)  # Default to 'first'
        
        keep_layout.addWidget(QLabel('When duplicates are found:'))
        keep_layout.addWidget(self.keep_combo)
        
        layout.addWidget(keep_group)
        
        # Preview section
        preview_group = QGroupBox('What This Will Do')
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet('background-color: #f8f9fa; border: 1px solid #ddd;')
        
        preview_layout.addWidget(self.preview_text)
        layout.addWidget(preview_group)
        
        # Update preview initially
        self._update_preview()
        
        # Connect signals to update preview
        self.method_group.buttonClicked.connect(self._update_preview)
        self.keep_combo.currentTextChanged.connect(self._update_preview)
        self.column_list.itemChanged.connect(self._update_preview)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _on_method_changed(self):
        """Handle method selection change."""
        method_id = self.method_group.checkedId()
        
        if method_id in [1, 2]:  # Selected columns or case-insensitive
            self.column_group.setEnabled(True)
        else:
            self.column_group.setEnabled(False)
        
        # Disable keep combo for smart seller creation (it has its own logic)
        if method_id == 4:  # Smart seller creation
            self.keep_combo.setEnabled(False)
        else:
            self.keep_combo.setEnabled(True)
        
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview text based on current settings."""
        method_id = self.method_group.checkedId()
        keep_text = self.keep_combo.currentText().split(' - ')[0]
        
        if method_id == 0:  # All columns
            method_desc = "all columns"
        elif method_id == 1:  # Selected columns
            selected_cols = self._get_selected_columns()
            if selected_cols:
                method_desc = f"columns: {', '.join(selected_cols)}"
            else:
                method_desc = "selected columns (none selected yet)"
        elif method_id == 2:  # Case-insensitive
            selected_cols = self._get_selected_columns()
            if selected_cols:
                method_desc = f"columns: {', '.join(selected_cols)} (case-insensitive)"
            else:
                method_desc = "all columns (case-insensitive)"
        elif method_id == 3:  # Address-based grouping
            method_desc = "Property Address grouping"
        elif method_id == 4:  # Smart seller creation
            method_desc = "Smart Seller Creation with phone prioritization"
        else:
            method_desc = "unknown method"
        
        keep_desc = {
            'first': 'keep the first occurrence',
            'last': 'keep the last occurrence', 
            'False': 'remove all duplicate rows'
        }.get(keep_text, keep_text)
        
        if method_id == 3:  # Address-based grouping
            preview = f"""Will group records by Property Address.
For each address group:
• If identical rows (same seller + phones) → Remove duplicates
• If different sellers → Create Seller 1,2,3,4,5 structure
• Apply phone prioritization to each seller

Example: Address "123 Main St" with 3 different sellers:
• Creates 1 record with Seller 1, Seller 2, Seller 3
• Each seller gets prioritized phones (Phone 1-5)"""
        elif method_id == 4:  # Smart seller creation
            preview = f"""Will create Pete-ready Seller 1-5 structure:
• Group by Property Address
• Remove full duplicates (same seller + phones)
• Create Seller 1-5 from address duplicates
• Apply phone prioritization (CORRECT > UNKNOWN > etc.)
• Concatenate emails per seller
• Hold additional sellers for future Pete processing

Example: 3 sellers at same address → 1 Pete record with Seller 1-5"""
        else:
            preview = f"""Will identify duplicate rows based on {method_desc}.
When duplicates are found, will {keep_desc}.

Example: If rows 5, 12, and 23 are duplicates:
• first: Keep row 5, remove rows 12 and 23
• last: Keep row 23, remove rows 5 and 12  
• False: Remove all rows 5, 12, and 23"""
        
        self.preview_text.setPlainText(preview)
    
    def _get_selected_columns(self) -> List[str]:
        """Get list of selected columns."""
        selected = []
        for i in range(self.column_list.count()):
            item = self.column_list.item(i)
            if item.checkState() == Qt.Checked:
                selected.append(item.text())
        return selected
    
    def _validate_and_accept(self):
        """Validate settings and create configuration."""
        method_id = self.method_group.checkedId()
        
        if method_id == 1:  # Selected columns
            selected_cols = self._get_selected_columns()
            if not selected_cols:
                # Show error - no columns selected
                return
        
        # Get keep parameter
        keep_text = self.keep_combo.currentText().split(' - ')[0]
        if keep_text == 'False':
            keep = False
        else:
            keep = keep_text
        
        # Create configuration
        if method_id == 0:
            self.config = {
                'method': 'all_columns',
                'keep': keep,
                'columns': None
            }
        elif method_id == 1:
            self.config = {
                'method': 'selected_columns', 
                'keep': keep,
                'columns': self._get_selected_columns()
            }
        elif method_id == 2:
            self.config = {
                'method': 'ignore_case',
                'keep': keep,
                'columns': self._get_selected_columns() if self._get_selected_columns() else None
            }
        elif method_id == 3:
            self.config = {
                'method': 'address_based_grouping',
                'keep': keep,
                'columns': None
            }
        elif method_id == 4:
            self.config = {
                'method': 'smart_seller_creation',
                'keep': 'first',  # Always keep first for smart seller creation
                'columns': None
            }
        
        self.accept()
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get the duplicate removal configuration."""
        return self.config