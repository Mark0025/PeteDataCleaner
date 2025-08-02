"""
Mapping UI Component

Main component for interactive column mapping between upload data and Pete headers.
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Tuple
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QHBoxLayout, QToolButton, QComboBox, 
    QTableWidgetItem, QAbstractItemView, QDialog, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from frontend.components.base_component import BaseComponent
from frontend.components.mapping_table_widget import MappingTableWidget
from frontend.dialogs.rule_mapping_dialog import RuleMappingDialog
from frontend.dialogs.concatenation_dialog import ConcatenationDialog
from backend.utils.data_standardizer import DataStandardizer

class MappingUI(BaseComponent):
    """
    Interactive mapping interface for column mapping.
    
    Features:
    - Toggle between upload and Pete header views
    - Interactive mapping with dropdowns
    - Rule editing capabilities
    - Context menu operations
    """
    
    def __init__(self, parent=None, df: Optional[pd.DataFrame] = None, 
                 pete_headers: Optional[List[str]] = None, 
                 rules: Optional[Dict[str, Any]] = None,
                 on_back: Optional[Callable] = None, 
                 on_exit: Optional[Callable] = None, 
                 on_settings: Optional[Callable] = None):
        """
        Initialize mapping UI.
        
        Args:
            parent: Parent widget
            df: Upload DataFrame to map
            pete_headers: List of Pete header names
            rules: Mapping rules configuration
            on_back: Callback for back button
            on_exit: Callback for exit button
            on_settings: Callback for settings button
        """
        super().__init__(parent, show_logo=True, show_navigation=True, 
                         on_back=on_back, on_exit=on_exit)
        
        if df is None or pete_headers is None:
            raise ValueError("DataFrame and Pete headers are required")
        
        self.df = df
        self.pete_headers = pete_headers
        self.rules = rules or {}
        self.on_settings = on_settings
        
        # Initialize backend standardizer
        self.standardizer = DataStandardizer(pete_headers)
        self.standardizer.rules = self.rules
        self.mapping = self.standardizer.propose_mapping(list(df.columns))
        
        self._setup_ui()
        self.update_mapping_table()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Header with controls
        header_layout = QHBoxLayout()
        
        # Toggle button for view mode
        self.toggle_btn = QPushButton('Show Upload Headers')
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_headers)
        
        header_layout.addWidget(QLabel('Mapping UI'))
        header_layout.addWidget(self.toggle_btn)
        
        # Settings button
        if self.on_settings:
            settings_btn = QToolButton()
            settings_btn.setIcon(QIcon.fromTheme('preferences-system'))
            settings_btn.setToolTip('Settings')
            settings_btn.clicked.connect(self.on_settings)
            header_layout.addWidget(settings_btn)
        
        # Edit rules button
        self.edit_rules_btn = QPushButton('Edit Mapping Rules')
        self.edit_rules_btn.clicked.connect(self.edit_mapping_rules)
        header_layout.addWidget(self.edit_rules_btn)
        
        self.layout.addLayout(header_layout)
        
        # Mapping table
        self.mapping_table = MappingTableWidget()
        self.mapping_table.set_pete_headers(self.pete_headers)
        
        # Connect signals
        self.mapping_table.columns_concatenation_requested.connect(
            self.handle_concatenation_request
        )
        self.mapping_table.column_rename_requested.connect(
            self.handle_rename_request
        )
        
        self.layout.addWidget(self.mapping_table)
    
    def toggle_headers(self):
        """Toggle between upload and Pete header views."""
        if self.toggle_btn.isChecked():
            self.toggle_btn.setText('Show Pete Headers')
        else:
            self.toggle_btn.setText('Show Upload Headers')
        self.update_mapping_table()
    
    def update_mapping_table(self):
        """Update the mapping table based on current view mode."""
        show_upload = self.toggle_btn.isChecked()
        
        # Clear existing table
        self.mapping_table.clear()
        self.mapping_table.setRowCount(0)
        self.mapping_table.setColumnCount(0)
        
        # Improve table styling for better readability
        self.mapping_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                alternate-background-color: #f8f9fa;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background-color: #1976d2;
                color: white;
                padding: 10px;
                border: 1px solid #1565c0;
                font-weight: bold;
                font-size: 13px;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #1976d2;
            }
        """)
        
        if show_upload:
            self._setup_upload_view()
        else:
            self._setup_pete_view()
        
        # Make headers more readable
        self.mapping_table.resizeColumnsToContents()
        self.mapping_table.horizontalHeader().setStretchLastSection(True)
        
        # Set minimum column widths for readability
        header = self.mapping_table.horizontalHeader()
        for i in range(self.mapping_table.columnCount()):
            current_width = self.mapping_table.columnWidth(i)
            min_width = 150  # Minimum 150px for readability
            if current_width < min_width:
                self.mapping_table.setColumnWidth(i, min_width)
    
    def _setup_upload_view(self):
        """Setup view showing upload columns as rows."""
        columns = ['Upload Column', 'Mapped Pete Header', 'Rule/Reason']
        self.mapping_table.setColumnCount(len(columns))
        self.mapping_table.setHorizontalHeaderLabels(columns)
        
        data = []
        for col in self.df.columns:
            mapping_info = self.mapping.get(col, (None, 0.0, 'No mapping'))
            pete_header, confidence, reason = mapping_info
            data.append([col, pete_header or '', reason])
        
        self.mapping_table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.mapping_table.setItem(row_idx, col_idx, item)
            
            # Add dropdown for Pete header selection
            combo = QComboBox()
            combo.addItem('')
            combo.addItems(self.pete_headers)
            
            current_pete = self.mapping.get(self.df.columns[row_idx], (None,))[0]
            if current_pete:
                combo.setCurrentText(current_pete)
            
            combo.currentTextChanged.connect(
                lambda val, c=self.df.columns[row_idx]: self.update_mapping_from_upload(c, val)
            )
            self.mapping_table.setCellWidget(row_idx, 1, combo)
    
    def _setup_pete_view(self):
        """Setup view showing Pete headers as rows."""
        columns = ['Pete Header', 'Mapped Upload Column', 'Rule/Reason']
        self.mapping_table.setColumnCount(len(columns))
        self.mapping_table.setHorizontalHeaderLabels(columns)
        
        # Create reverse mapping
        reverse_map = {}
        for col, (pete, confidence, reason) in self.mapping.items():
            if pete:
                reverse_map[pete] = (col, reason)
        
        data = []
        for pete in self.pete_headers:
            mapped_col, reason = reverse_map.get(pete, ('', 'No match'))
            data.append([pete, mapped_col, reason])
        
        self.mapping_table.setRowCount(len(data))
        for row_idx, row in enumerate(data):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.mapping_table.setItem(row_idx, col_idx, item)
            
            # Add dropdown for upload column selection
            combo = QComboBox()
            combo.addItem('')
            combo.addItems(list(self.df.columns))
            
            # Find current mapping
            pete_header = self.pete_headers[row_idx]
            mapped_col = ''
            for col, (mapped_pete, _, _) in self.mapping.items():
                if mapped_pete == pete_header:
                    mapped_col = col
                    break
            
            if mapped_col:
                combo.setCurrentText(mapped_col)
            
            combo.currentTextChanged.connect(
                lambda val, p=pete_header: self.update_mapping_from_pete(p, val)
            )
            self.mapping_table.setCellWidget(row_idx, 1, combo)
    
    def update_mapping_from_upload(self, col: str, pete: str):
        """Update mapping from upload column perspective."""
        # Enforce one-to-one mapping
        for c in self.mapping:
            if self.mapping[c][0] == pete and c != col and pete:
                self.mapping[c] = (None, 0.0, 'Unmapped (duplicate)')
        
        if pete:
            reason = 'Manual'
        else:
            reason = 'Manual skip'
        
        self.mapping[col] = (pete if pete else None, 100.0 if pete else 0.0, reason)
        self.update_mapping_table()
    
    def update_mapping_from_pete(self, pete: str, col: str):
        """Update mapping from Pete header perspective."""
        # Clear existing mapping to this Pete header
        for c in self.mapping:
            if self.mapping[c][0] == pete:
                self.mapping[c] = (None, 0.0, 'Manual skip')
        
        if col:
            self.mapping[col] = (pete, 100.0, 'Manual')
        
        self.update_mapping_table()
    
    def edit_mapping_rules(self):
        """Open dialog to edit mapping rules."""
        rule_dialog = RuleMappingDialog(
            current_rules=self.rules,
            upload_columns=list(self.df.columns),
            pete_headers=self.pete_headers,
            parent=self
        )
        
        if rule_dialog.exec_() == QDialog.Accepted:
            # Update rules
            self.rules = rule_dialog.get_updated_rules()
            
            # Rerun mapping with new rules
            self.standardizer.rules = self.rules
            self.mapping = self.standardizer.propose_mapping(list(self.df.columns))
            
            # Update table
            self.update_mapping_table()
    
    def handle_concatenation_request(self, source_columns: List[str], 
                                   destination_header: str, separator: str):
        """Handle concatenation request from table widget."""
        # Update rules
        concat_fields = self.rules.get('concat_fields', {})
        concat_fields[destination_header] = source_columns
        self.rules['concat_fields'] = concat_fields
        self.rules['concat_separator'] = separator
        
        # Rerun mapping
        self.standardizer.rules = self.rules
        self.mapping = self.standardizer.propose_mapping(list(self.df.columns))
        
        # Update table
        self.update_mapping_table()
        
        # Show confirmation
        QMessageBox.information(
            self,
            'Concatenation Added',
            f"Concatenated {' + '.join(source_columns)} to {destination_header}"
        )
    
    def handle_rename_request(self, old_name: str, new_name: str):
        """Handle column rename request from table widget."""
        try:
            # Rename column in DataFrame
            self.df.rename(columns={old_name: new_name}, inplace=True)
            
            # Update mapping
            if old_name in self.mapping:
                mapping_info = self.mapping[old_name]
                del self.mapping[old_name]
                self.mapping[new_name] = mapping_info
            
            # Refresh mapping
            self.mapping = self.standardizer.propose_mapping(list(self.df.columns))
            self.update_mapping_table()
            
            QMessageBox.information(
                self,
                'Column Renamed',
                f'Column "{old_name}" renamed to "{new_name}"'
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                'Rename Error',
                f'Failed to rename column: {str(e)}'
            )
    
    def get_mapping(self) -> Dict[str, Tuple[Optional[str], float, str]]:
        """Get current mapping configuration."""
        return self.mapping.copy()
    
    def get_transformed_data(self) -> pd.DataFrame:
        """Get transformed data according to current mapping."""
        return self.standardizer.transform_data(self.df, self.mapping)