"""
Rule Mapping Dialog

Complex dialog for editing mapping rules dynamically with tabbed interface
for different rule types: Never Map, Explicit Map, and Concatenation.
"""

from typing import Dict, List, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QListWidget, QListWidgetItem,
    QLabel, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
    QDialogButtonBox
)
from PyQt5.QtCore import Qt

class RuleMappingDialog(QDialog):
    """
    Dialog for editing mapping rules dynamically.
    
    Provides tabbed interface for:
    - Never Map: Columns to exclude from mapping
    - Explicit Map: Direct column-to-header mappings
    - Concatenation: Rules for combining multiple columns
    """
    
    def __init__(self, current_rules: Dict[str, Any], upload_columns: List[str], 
                 pete_headers: List[str], parent=None):
        """
        Initialize rule mapping dialog.
        
        Args:
            current_rules: Current mapping rules configuration
            upload_columns: List of upload column names
            pete_headers: List of Pete header names
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle('Edit Mapping Rules')
        
        self.current_rules = current_rules.copy()
        self.upload_columns = upload_columns
        self.pete_headers = pete_headers
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface with tabbed layout."""
        layout = QVBoxLayout()
        
        # Tabs for different rule types
        self.tab_widget = QTabWidget()
        
        # Setup tabs
        self._setup_never_map_tab()
        self._setup_explicit_map_tab()
        self._setup_concatenation_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_rules)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _setup_never_map_tab(self):
        """Setup the Never Map tab."""
        never_map_widget = QWidget()
        never_map_layout = QVBoxLayout()
        
        self.never_map_list = QListWidget()
        self.never_map_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Populate Never Map list
        current_never_map = self.current_rules.get('never_map', [])
        for col in self.upload_columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if col in current_never_map else Qt.Unchecked)
            self.never_map_list.addItem(item)
        
        never_map_layout.addWidget(QLabel('Select columns to exclude from mapping:'))
        never_map_layout.addWidget(self.never_map_list)
        never_map_widget.setLayout(never_map_layout)
        
        self.tab_widget.addTab(never_map_widget, 'Never Map')
    
    def _setup_explicit_map_tab(self):
        """Setup the Explicit Map tab."""
        explicit_map_widget = QWidget()
        explicit_map_layout = QVBoxLayout()
        
        self.explicit_map_table = QTableWidget()
        self.explicit_map_table.setColumnCount(2)
        self.explicit_map_table.setHorizontalHeaderLabels(['Upload Column', 'Pete Header'])
        
        # Populate Explicit Map table
        explicit_map = self.current_rules.get('explicit_map', {})
        self.explicit_map_table.setRowCount(len(self.upload_columns))
        
        for row, col in enumerate(self.upload_columns):
            # Upload column (read-only)
            upload_item = QTableWidgetItem(col)
            upload_item.setFlags(upload_item.flags() & ~Qt.ItemIsEditable)
            self.explicit_map_table.setItem(row, 0, upload_item)
            
            # Pete header dropdown
            pete_combo = QComboBox()
            pete_combo.addItem('')  # Allow no mapping
            pete_combo.addItems(self.pete_headers)
            
            # Set current mapping if exists
            current_mapping = next(
                (pete for upload, pete in explicit_map.items() 
                 if upload.lower() == col.lower()), 
                ''
            )
            if current_mapping:
                pete_combo.setCurrentText(current_mapping)
            
            self.explicit_map_table.setCellWidget(row, 1, pete_combo)
        
        explicit_map_layout.addWidget(QLabel('Map upload columns to specific Pete headers:'))
        explicit_map_layout.addWidget(self.explicit_map_table)
        explicit_map_widget.setLayout(explicit_map_layout)
        
        self.tab_widget.addTab(explicit_map_widget, 'Explicit Map')
    
    def _setup_concatenation_tab(self):
        """Setup the Concatenation tab."""
        concat_widget = QWidget()
        concat_layout = QVBoxLayout()
        
        self.concat_table = QTableWidget()
        self.concat_table.setColumnCount(3)
        self.concat_table.setHorizontalHeaderLabels(['Pete Header', 'Source Columns', 'Separator'])
        
        concat_fields = self.current_rules.get('concat_fields', {})
        self.concat_table.setRowCount(len(concat_fields) + 1)  # Extra row for adding new
        
        for row, (pete_header, source_cols) in enumerate(concat_fields.items()):
            # Pete header dropdown
            pete_combo = QComboBox()
            pete_combo.addItems(self.pete_headers)
            pete_combo.setCurrentText(pete_header)
            self.concat_table.setCellWidget(row, 0, pete_combo)
            
            # Source columns multiselect
            source_list = QListWidget()
            source_list.setSelectionMode(QListWidget.MultiSelection)
            for col in self.upload_columns:
                item = QListWidgetItem(col)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if col in source_cols else Qt.Unchecked)
                source_list.addItem(item)
            self.concat_table.setCellWidget(row, 1, source_list)
            
            # Separator input
            separator_input = QLineEdit(self.current_rules.get('concat_separator', ' '))
            self.concat_table.setCellWidget(row, 2, separator_input)
        
        concat_layout.addWidget(QLabel('Configure column concatenation:'))
        concat_layout.addWidget(self.concat_table)
        concat_widget.setLayout(concat_layout)
        
        self.tab_widget.addTab(concat_widget, 'Concatenation')
    
    def save_rules(self):
        """Save the configured rules and close dialog."""
        # Never Map
        never_map = [
            self.never_map_list.item(i).text() 
            for i in range(self.never_map_list.count()) 
            if self.never_map_list.item(i).checkState() == Qt.Checked
        ]
        
        # Explicit Map
        explicit_map = {}
        for row in range(self.explicit_map_table.rowCount()):
            upload_col = self.explicit_map_table.item(row, 0).text()
            pete_combo = self.explicit_map_table.cellWidget(row, 1)
            pete_header = pete_combo.currentText()
            
            if pete_header:
                explicit_map[upload_col] = pete_header
        
        # Concatenation
        concat_fields = {}
        concat_separator = ' '  # Default
        for row in range(self.concat_table.rowCount()):
            pete_combo = self.concat_table.cellWidget(row, 0)
            source_list = self.concat_table.cellWidget(row, 1)
            separator_input = self.concat_table.cellWidget(row, 2)
            
            pete_header = pete_combo.currentText() if pete_combo else ''
            if separator_input:
                concat_separator = separator_input.text()
            
            if source_list:
                source_cols = [
                    source_list.item(i).text() 
                    for i in range(source_list.count()) 
                    if source_list.item(i).checkState() == Qt.Checked
                ]
                
                if pete_header and source_cols:
                    concat_fields[pete_header] = source_cols
        
        # Update rules
        self.current_rules['never_map'] = never_map
        self.current_rules['explicit_map'] = explicit_map
        self.current_rules['concat_fields'] = concat_fields
        self.current_rules['concat_separator'] = concat_separator
        
        self.accept()
    
    def get_updated_rules(self) -> Dict[str, Any]:
        """Get the updated rules after dialog completion."""
        return self.current_rules