import os
import sys
import shutil
import pandas as pd
from loguru import logger
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea, QListWidget, QListWidgetItem,
    QDialog, QFormLayout, QSpinBox, QCheckBox, QDialogButtonBox, QToolButton, QInputDialog, QDoubleSpinBox,
    QTabWidget, QLineEdit, QAbstractItemView, QMenu, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from backend.utils.data_standardizer import DataStandardizer
from backend.sheets_client import SheetsClient
import re
from backend.utils.data_type_converter import DataTypeConverter
from typing import Dict, List, Any, Optional

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'upload')
logger.add(os.path.join(os.path.dirname(__file__), '..', 'DEV_MAN', 'backend.log'), level='INFO')

# Dummy backend rules config for demonstration (replace with DataStandardizer integration)
rules_config = {
    'fuzzy_threshold': 80,
    'preview_row_count': 10,
    'preview_col_count': 10,
    'show_not_mapped_in_report': True,
    'disable_fuzzy': False,
    'empty_column_config': {
        'filter_empty_columns': True,
        'empty_column_threshold': 0.9
    }
}

CLI_OPTIONS = [
    ("Workspace", "Manage Google Sheets workspace (list, search, add, select, browse)"),
    ("Standardize", "Standardize uploaded data files to Pete template"),
    ("Rules", "Rule management utilities (coming soon)"),
    ("Backend", "Backend/analysis utilities (coming soon)"),
    ("Test", "Run all tests and show what's working"),
    ("GUI Mapping Tool", "Launch the GUI mapping tool for visual column mapping"),
    ("Exit", "Exit the application")
]

LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'public', 'pete.png')

def create_logo_label():
    label = QLabel()
    pixmap = QPixmap(LOGO_PATH)
    if not pixmap.isNull():
        pixmap = pixmap.scaledToHeight(60, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
    else:
        label.setText('PETE')
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet('font-size: 32px; font-weight: bold; color: #1976d2;')
    return label

class SettingsDialog(QDialog):
    def __init__(self, parent=None, rules=None, menu_options=None, on_save=None):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setModal(True)
        self.rules = rules or {}
        self.menu_options = menu_options or {}
        self.on_save = on_save
        layout = QFormLayout(self)
        
        # Mapping/preview settings
        self.fuzzy_spin = QSpinBox()
        self.fuzzy_spin.setRange(0, 100)
        self.fuzzy_spin.setValue(self.rules.get('fuzzy_threshold', 80))
        self.fuzzy_spin.setToolTip('Minimum similarity for fuzzy matching (0-100)')
        layout.addRow('Fuzzy Threshold:', self.fuzzy_spin)
        
        self.row_spin = QSpinBox()
        self.row_spin.setRange(1, 100)
        self.row_spin.setValue(self.rules.get('preview_row_count', 10))
        self.row_spin.setToolTip('Number of rows to preview in tables')
        layout.addRow('Preview Row Count:', self.row_spin)
        
        self.col_spin = QSpinBox()
        self.col_spin.setRange(1, 100)
        self.col_spin.setValue(self.rules.get('preview_col_count', 10))
        self.col_spin.setToolTip('Number of columns to preview in tables')
        layout.addRow('Preview Column Count:', self.col_spin)
        
        self.show_unmapped = QCheckBox('Show Unmapped Columns in Report')
        self.show_unmapped.setChecked(self.rules.get('show_not_mapped_in_report', True))
        self.show_unmapped.setToolTip('Include unmapped columns in reports and previews')
        layout.addRow(self.show_unmapped)
        
        self.disable_fuzzy = QCheckBox('Disable Fuzzy Matching')
        self.disable_fuzzy.setChecked(self.rules.get('disable_fuzzy', False))
        self.disable_fuzzy.setToolTip('Turn off fuzzy matching for mapping')
        layout.addRow(self.disable_fuzzy)
        
        # Empty column filtering settings
        layout.addRow(QLabel('<b>Empty Column Filtering</b>'))
        
        self.filter_empty_columns = QCheckBox('Filter Empty Columns')
        empty_column_config = self.rules.get('empty_column_config', {})
        self.filter_empty_columns.setChecked(empty_column_config.get('filter_empty_columns', True))
        self.filter_empty_columns.setToolTip('Remove columns with mostly NaN/empty values')
        layout.addRow(self.filter_empty_columns)
        
        self.empty_threshold_spin = QDoubleSpinBox()
        self.empty_threshold_spin.setRange(0.0, 1.0)
        self.empty_threshold_spin.setSingleStep(0.1)
        self.empty_threshold_spin.setValue(empty_column_config.get('empty_column_threshold', 0.9))
        self.empty_threshold_spin.setToolTip('Percentage of NaN/empty values to consider for column removal (0.0-1.0)')
        layout.addRow('Empty Column Threshold:', self.empty_threshold_spin)
        
        # Menu options toggles
        layout.addRow(QLabel('<b>Menu Options</b>'))
        self.menu_checkboxes = {}
        for key, (label, visible) in self.menu_options.items():
            cb = QCheckBox(f'Show "{label}" on main menu')
            cb.setChecked(visible)
            self.menu_checkboxes[key] = cb
            layout.addRow(cb)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def save(self):
        # Update rules with new settings
        self.rules['fuzzy_threshold'] = self.fuzzy_spin.value()
        self.rules['preview_row_count'] = self.row_spin.value()
        self.rules['preview_col_count'] = self.col_spin.value()
        self.rules['show_not_mapped_in_report'] = self.show_unmapped.isChecked()
        self.rules['disable_fuzzy'] = self.disable_fuzzy.isChecked()
        
        # Empty column filtering configuration
        self.rules['empty_column_config'] = {
            'filter_empty_columns': self.filter_empty_columns.isChecked(),
            'empty_column_threshold': self.empty_threshold_spin.value()
        }
        
        # Menu options
        menu_opts = {k: (lbl, cb.isChecked()) for k, (lbl, cb) in zip(self.menu_options.keys(), [(v[0], self.menu_checkboxes[k]) for k, v in self.menu_options.items()])}
        
        if self.on_save:
            self.on_save(self.rules, menu_opts)
        
        self.accept()

class StartupMenu(QWidget):
    def __init__(self, parent=None, on_select=None, options=None):
        super().__init__(parent)
        self.setWindowTitle('Pete Main Menu')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(create_logo_label())
        self.label = QLabel('Pete Main Menu')
        self.label.setStyleSheet('font-weight: bold; font-size: 18px;')
        self.layout.addWidget(self.label)
        self.buttons = []
        self.options = options or CLI_OPTIONS
        for name, desc in self.options:
            btn = QPushButton(f"{name} - {desc}")
            btn.clicked.connect(lambda checked, n=name: self.handle_select(n))
            self.layout.addWidget(btn)
            self.buttons.append(btn)
        self.on_select = on_select
    def handle_select(self, name):
        if self.on_select:
            self.on_select(name)

class FileSelector(QWidget):
    def __init__(self, parent=None, on_exit=None):
        super().__init__(parent)
        self.setWindowTitle('Pete GUI Mapping Tool - File Selection')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(create_logo_label())
        self.label = QLabel('Select a data file from upload/ or upload a new CSV:')
        self.layout.addWidget(self.label)
        self.file_combo = QComboBox()
        self.layout.addWidget(self.file_combo)
        btn_layout = QHBoxLayout()
        self.upload_btn = QPushButton('Upload New CSV')
        self.refresh_btn = QPushButton('Refresh List')
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.refresh_btn)
        self.layout.addLayout(btn_layout)
        self.status_label = QLabel('')
        self.layout.addWidget(self.status_label)
        self.preview_btn = QPushButton('Preview Table')
        self.preview_btn.setEnabled(False)
        self.layout.addWidget(self.preview_btn)
        self.map_btn = QPushButton('Map to Pete Headers')
        self.map_btn.setEnabled(False)
        self.layout.addWidget(self.map_btn)
        self.exit_btn = QPushButton('Exit')
        self.layout.addWidget(self.exit_btn)
        self.file_combo.currentIndexChanged.connect(self.on_file_selected)
        self.upload_btn.clicked.connect(self.upload_new_csv)
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        self.preview_btn.clicked.connect(self.preview_table)
        self.map_btn.clicked.connect(self.map_to_pete_headers)
        self.exit_btn.clicked.connect(self.handle_exit)
        self.selected_file = None
        self.table_widget = None
        self.df = None
        self.on_exit = on_exit
        self.refresh_file_list()
    def refresh_file_list(self):
        files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(('.csv', '.xlsx', '.xls'))]
        self.file_combo.clear()
        self.file_combo.addItems([''] + files)
        self.status_label.setText('File list refreshed.')
        logger.info('File list refreshed.')
        self.preview_btn.setEnabled(False)
        self.map_btn.setEnabled(False)
        self.selected_file = None
    def on_file_selected(self, idx):
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
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select CSV file to upload', '', 'CSV Files (*.csv)')
        if file_path:
            try:
                dest_path = os.path.join(UPLOAD_DIR, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)
                logger.success(f"Uploaded new CSV: {file_path} -> {dest_path}")
                self.status_label.setText(f"Uploaded: {os.path.basename(file_path)}")
                self.refresh_file_list()
            except Exception as e:
                logger.error(f"Failed to upload CSV: {e}")
                self.status_label.setText(f"Error: {e}")
    def preview_table(self):
        if not self.selected_file:
            QMessageBox.warning(self, 'No file selected', 'Please select a file to preview.')
            return
        file_path = os.path.join(UPLOAD_DIR, self.selected_file)
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_path)
            else:
                QMessageBox.warning(self, 'Unsupported file', f'Unsupported file type: {ext}')
                return
        except Exception as ex:
            logger.error(f'Error reading file: {ex}')
            QMessageBox.critical(self, 'Error', f'Error reading file: {ex}')
            return
        self.df = df  # Store DataFrame as attribute for later use
        if self.table_widget:
            self.layout.removeWidget(self.table_widget)
            self.table_widget.deleteLater()
            self.table_widget = None
        self.table_widget = QTableWidget()
        preview_rows = min(rules_config.get('preview_row_count', 10), len(df))
        preview_cols = len(df.columns)
        self.table_widget.setRowCount(preview_rows)
        self.table_widget.setColumnCount(preview_cols)
        self.table_widget.setHorizontalHeaderLabels([str(col) for col in df.columns])
        for i in range(preview_rows):
            for j in range(preview_cols):
                val = str(df.iloc[i, j]) if j < len(df.columns) else ''
                self.table_widget.setItem(i, j, QTableWidgetItem(val))
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.layout.addWidget(self.table_widget)
        self.status_label.setText(f'Previewing: {self.selected_file}')
        logger.info(f'Previewed file: {self.selected_file}')
        self.map_btn.setEnabled(True)
    def map_to_pete_headers(self):
        if self.df is not None:
            try:
                # Default Pete template sheet details
                DEFAULT_SHEET_ID = '11M1wYpVdfQfZOM3y5GSVj75FuYCQ0qVtOt4MbUpbZzw'
                DEFAULT_TAB_NAME = 'Sheet1'

                # Fetch Pete headers from backend (Google Sheet)
                sheet_id = os.getenv('PETE_ADDRESS_TEMPLATE_SHEET_ID', DEFAULT_SHEET_ID)
                tab_name = os.getenv('PETE_ADDRESS_TEMPLATE_SHEET_NAME', DEFAULT_TAB_NAME).replace('"', '')

                # If sheet_id or tab_name not set, use default or prompt user
                if not sheet_id or not tab_name:
                    # Use SheetsClient to load workspace
                    workspace = SheetsClient.load_workspace()
                    
                    # If no sheets in workspace, use default
                    if not workspace.get("sheets", []):
                        sheet_id = DEFAULT_SHEET_ID
                        tab_name = DEFAULT_TAB_NAME
                    else:
                        # Create a custom dialog to mimic backend's interactive selection
                        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget

                        class WorkspaceDialog(QDialog):
                            def __init__(self, workspace, parent=None):
                                super().__init__(parent)
                                self.setWindowTitle('Select Google Sheet')
                                self.layout = QVBoxLayout()
                                
                                # Title
                                title_label = QLabel("=== Google Workspace ===")
                                self.layout.addWidget(title_label)
                                
                                # List of sheets
                                self.sheet_list = QListWidget()
                                for sheet in workspace['sheets']:
                                    item_text = f"{sheet['spreadsheet_name']} (ID: {sheet['sheet_id']}) Tabs: {', '.join(sheet['tabs'])} Last used: {sheet['last_used']}"
                                    self.sheet_list.addItem(item_text)
                                self.layout.addWidget(self.sheet_list)
                                
                                # Buttons
                                btn_layout = QVBoxLayout()
                                default_btn = QPushButton('Use Default Pete Template')
                                default_btn.clicked.connect(self.use_default)
                                select_btn = QPushButton('Select Sheet')
                                select_btn.clicked.connect(self.accept)
                                manual_btn = QPushButton('Enter Sheet ID Manually')
                                manual_btn.clicked.connect(self.manual_entry)
                                
                                btn_layout.addWidget(default_btn)
                                btn_layout.addWidget(select_btn)
                                btn_layout.addWidget(manual_btn)
                                self.layout.addLayout(btn_layout)
                                
                                self.setLayout(self.layout)
                                self.selected_sheet_id = None
                                self.selected_tab_name = None
                            
                            def use_default(self):
                                self.selected_sheet_id = DEFAULT_SHEET_ID
                                self.selected_tab_name = DEFAULT_TAB_NAME
                                self.accept()
                            
                            def manual_entry(self):
                                sheet_id, ok = QInputDialog.getText(self, 'Enter Sheet ID', 'Google Sheet ID:')
                                if ok and sheet_id:
                                    self.selected_sheet_id = sheet_id
                                    # Prompt for tab name
                                    client = SheetsClient()
                                    client.set_sheet_id(sheet_id)
                                    sheet_names = client.get_sheet_names()
                                    if sheet_names:
                                        tab_name, ok = QInputDialog.getItem(
                                            self, 
                                            'Select Sheet Tab', 
                                            'Choose the tab containing headers:', 
                                            sheet_names, 
                                            0, 
                                            False
                                        )
                                        if ok and tab_name:
                                            self.selected_tab_name = tab_name
                                            self.accept()
                            
                            def accept(self):
                                if not self.selected_sheet_id:
                                    # If no manual entry, use selected list item
                                    current_item = self.sheet_list.currentItem()
                                    if current_item:
                                        # Extract sheet ID from the displayed text
                                        sheet_id_match = re.search(r'\(ID: (.*?)\)', current_item.text())
                                        if sheet_id_match:
                                            self.selected_sheet_id = sheet_id_match.group(1)
                                            # Get first tab for the selected sheet
                                            client = SheetsClient()
                                            client.set_sheet_id(self.selected_sheet_id)
                                            sheet_names = client.get_sheet_names()
                                            if sheet_names:
                                                self.selected_tab_name = sheet_names[0]
                                super().accept()

                        # Show workspace dialog
                        workspace_dialog = WorkspaceDialog(workspace, self)
                        if workspace_dialog.exec_() == QDialog.Accepted:
                            sheet_id = workspace_dialog.selected_sheet_id
                            tab_name = workspace_dialog.selected_tab_name
                        else:
                            # Fallback to default if no selection
                            sheet_id = DEFAULT_SHEET_ID
                            tab_name = DEFAULT_TAB_NAME

                    # Set the sheet ID for the client
                    client = SheetsClient()
                    client.set_sheet_id(sheet_id)
                    client.log_sheet_to_workspace()

                # Fetch Pete headers
                pete_headers = DataStandardizer.load_pete_headers_from_sheet(sheet_id, tab_name)
                if not pete_headers:
                    raise ValueError('No Pete headers found in template sheet.')

                # Find the MainWindow parent and call its show_mapping_ui method
                parent_window = self
                while parent_window is not None:
                    if hasattr(parent_window, 'show_mapping_ui'):
                        parent_window.show_mapping_ui(self.df, pete_headers)
                        break
                    parent_window = parent_window.parent()
                
                # If no parent with show_mapping_ui found, raise an error
                if parent_window is None:
                    raise AttributeError("Could not find a parent window with show_mapping_ui method")

            except Exception as e:
                logger.error(f"Failed to fetch Pete headers: {e}")
                QMessageBox.critical(self, 'Error', f'Failed to fetch Pete headers: {e}')
    def handle_exit(self):
        if self.on_exit:
            self.on_exit()

class RuleMappingDialog(QDialog):
    """Dialog for editing mapping rules dynamically."""
    def __init__(self, current_rules: Dict[str, Any], upload_columns: List[str], pete_headers: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Mapping Rules')
        self.current_rules = current_rules.copy()
        self.upload_columns = upload_columns
        self.pete_headers = pete_headers
        
        layout = QVBoxLayout()
        
        # Tabs for different rule types
        self.tab_widget = QTabWidget()
        
        # Never Map Tab
        never_map_widget = QWidget()
        never_map_layout = QVBoxLayout()
        self.never_map_list = QListWidget()
        self.never_map_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Populate Never Map list
        for col in upload_columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if col in current_rules.get('never_map', []) else Qt.Unchecked)
            self.never_map_list.addItem(item)
        
        never_map_layout.addWidget(QLabel('Select columns to exclude from mapping:'))
        never_map_layout.addWidget(self.never_map_list)
        never_map_widget.setLayout(never_map_layout)
        
        # Explicit Map Tab
        explicit_map_widget = QWidget()
        explicit_map_layout = QVBoxLayout()
        
        self.explicit_map_table = QTableWidget()
        self.explicit_map_table.setColumnCount(2)
        self.explicit_map_table.setHorizontalHeaderLabels(['Upload Column', 'Pete Header'])
        
        # Populate Explicit Map table
        explicit_map = current_rules.get('explicit_map', {})
        self.explicit_map_table.setRowCount(len(upload_columns))
        for row, col in enumerate(upload_columns):
            # Upload column column
            upload_item = QTableWidgetItem(col)
            upload_item.setFlags(upload_item.flags() & ~Qt.ItemIsEditable)
            self.explicit_map_table.setItem(row, 0, upload_item)
            
            # Pete header dropdown
            pete_combo = QComboBox()
            pete_combo.addItem('')  # Allow no mapping
            pete_combo.addItems(pete_headers)
            
            # Set current mapping if exists
            current_mapping = next((pete for upload, pete in explicit_map.items() if upload.lower() == col.lower()), '')
            if current_mapping:
                pete_combo.setCurrentText(current_mapping)
            
            self.explicit_map_table.setCellWidget(row, 1, pete_combo)
        
        explicit_map_layout.addWidget(QLabel('Map upload columns to specific Pete headers:'))
        explicit_map_layout.addWidget(self.explicit_map_table)
        explicit_map_widget.setLayout(explicit_map_layout)
        
        # Concatenation Tab
        concat_widget = QWidget()
        concat_layout = QVBoxLayout()
        
        self.concat_table = QTableWidget()
        self.concat_table.setColumnCount(3)
        self.concat_table.setHorizontalHeaderLabels(['Pete Header', 'Source Columns', 'Separator'])
        
        concat_fields = current_rules.get('concat_fields', {})
        self.concat_table.setRowCount(len(concat_fields) + 1)  # Extra row for adding new
        
        for row, (pete_header, source_cols) in enumerate(concat_fields.items()):
            # Pete header dropdown
            pete_combo = QComboBox()
            pete_combo.addItems(pete_headers)
            pete_combo.setCurrentText(pete_header)
            self.concat_table.setCellWidget(row, 0, pete_combo)
            
            # Source columns multiselect
            source_list = QListWidget()
            source_list.setSelectionMode(QListWidget.MultiSelection)
            for col in upload_columns:
                item = QListWidgetItem(col)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if col in source_cols else Qt.Unchecked)
                source_list.addItem(item)
            self.concat_table.setCellWidget(row, 1, source_list)
            
            # Separator input
            separator_input = QLineEdit(current_rules.get('concat_separator', ' '))
            self.concat_table.setCellWidget(row, 2, separator_input)
        
        concat_layout.addWidget(QLabel('Configure column concatenation:'))
        concat_layout.addWidget(self.concat_table)
        concat_widget.setLayout(concat_layout)
        
        # Add tabs
        self.tab_widget.addTab(never_map_widget, 'Never Map')
        self.tab_widget.addTab(explicit_map_widget, 'Explicit Map')
        self.tab_widget.addTab(concat_widget, 'Concatenation')
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.save_rules)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def save_rules(self):
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
            concat_separator = separator_input.text() if separator_input else ' '
            
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

class ConcatenationDialog(QDialog):
    """Dialog for creating column concatenations."""
    def __init__(self, upload_columns: List[str], pete_headers: List[str], 
                 pre_selected_columns: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Concatenate Columns')
        self.upload_columns = upload_columns
        self.pete_headers = pete_headers
        self.result = None
        
        layout = QVBoxLayout()
        
        # Source Columns Selection
        source_layout = QHBoxLayout()
        self.source_cols = QListWidget()
        self.source_cols.setSelectionMode(QListWidget.MultiSelection)
        
        # Populate source columns
        for col in upload_columns:
            item = QListWidgetItem(col)
            self.source_cols.addItem(item)
            
            # Pre-select columns if provided
            if pre_selected_columns and col in pre_selected_columns:
                item.setSelected(True)
        
        source_layout.addWidget(QLabel('Select Columns to Concatenate:'))
        source_layout.addWidget(self.source_cols)
        layout.addLayout(source_layout)
        
        # Separator Input
        separator_layout = QHBoxLayout()
        separator_layout.addWidget(QLabel('Separator:'))
        self.separator_input = QLineEdit(' ')  # Default space separator
        separator_layout.addWidget(self.separator_input)
        layout.addLayout(separator_layout)
        
        # Destination Selection
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(QLabel('Map to Pete Header:'))
        self.dest_combo = QComboBox()
        self.dest_combo.addItems([''] + pete_headers)
        dest_layout.addWidget(self.dest_combo)
        layout.addLayout(dest_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def validate_and_accept(self):
        """Validate inputs and prepare result."""
        selected_cols = [
            item.text() for item in self.source_cols.selectedItems()
        ]
        separator = self.separator_input.text()
        dest_header = self.dest_combo.currentText()
        
        # Validate inputs
        if len(selected_cols) < 2:
            QMessageBox.warning(self, 'Invalid Input', 'Please select at least two columns to concatenate.')
            return
        
        if not dest_header:
            QMessageBox.warning(self, 'Invalid Input', 'Please select a destination Pete header.')
            return
        
        # Prepare result
        self.result = {
            'source_columns': selected_cols,
            'separator': separator,
            'destination_header': dest_header
        }
        
        self.accept()

class MappingTableWidget(QTableWidget):
    """Enhanced table widget with multi-select and context menu."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Enable multi-column selection
        self.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Enable right-click context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Track selected columns
        self.selected_columns = []

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Update selected columns
        self.selected_columns = []
        for index in self.selectedIndexes():
            col_name = self.horizontalHeaderItem(index.column()).text()
            if col_name not in self.selected_columns:
                self.selected_columns.append(col_name)

    def show_context_menu(self, pos):
        # Create context menu
        context_menu = QMenu(self)
        
        # Concatenate action (if 2+ columns selected)
        if len(self.selected_columns) > 1:
            concat_action = QAction('Concatenate Columns', self)
            concat_action.triggered.connect(self.open_concatenation_dialog)
            context_menu.addAction(concat_action)
        
        # Rename action (if 1 column selected)
        if len(self.selected_columns) == 1:
            rename_action = QAction('Rename Column', self)
            rename_action.triggered.connect(self.open_rename_dialog)
            context_menu.addAction(rename_action)
        
        # Show menu at cursor position
        context_menu.exec_(self.mapToGlobal(pos))

    def open_concatenation_dialog(self):
        # Open dialog to concatenate selected columns
        dialog = ConcatenationDialog(self.selected_columns, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            # Emit signal or call parent method to handle concatenation
            if hasattr(self.parent(), 'concatenate_columns'):
                self.parent().concatenate_columns(
                    dialog.source_columns, 
                    dialog.destination_column, 
                    dialog.separator
                )

    def open_rename_dialog(self):
        # Open dialog to rename selected column
        current_name = self.selected_columns[0]
        dialog = RenameColumnDialog(current_name, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            # Emit signal or call parent method to handle renaming
            if hasattr(self.parent(), 'rename_column'):
                self.parent().rename_column(
                    current_name, 
                    dialog.new_name
                )

class ConcatenationDialog(QDialog):
    def __init__(self, available_columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Concatenate Columns')
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Source columns selection
        source_layout = QHBoxLayout()
        source_label = QLabel('Source Columns:')
        self.source_list = QListWidget()
        self.source_list.setSelectionMode(QAbstractItemView.MultiSelection)
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_list)
        layout.addLayout(source_layout)
        
        # Populate source columns
        self.source_list.addItems(available_columns)
        
        # Separator input
        separator_layout = QHBoxLayout()
        separator_label = QLabel('Separator:')
        self.separator_input = QLineEdit(' ')  # Default space separator
        separator_layout.addWidget(separator_label)
        separator_layout.addWidget(self.separator_input)
        layout.addLayout(separator_layout)
        
        # Destination column selection
        dest_layout = QHBoxLayout()
        dest_label = QLabel('Destination Column:')
        self.dest_combo = QComboBox()
        self.dest_combo.addItems(available_columns)
        dest_layout.addWidget(dest_label)
        dest_layout.addWidget(self.dest_combo)
        layout.addLayout(dest_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Properties to store selected values
        self.source_columns = []
        self.destination_column = ''
        self.separator = ' '
    
    def accept(self):
        # Validate and store selected values
        self.source_columns = [
            item.text() for item in self.source_list.selectedItems()
        ]
        self.destination_column = self.dest_combo.currentText()
        self.separator = self.separator_input.text()
        
        # Ensure at least two source columns are selected
        if len(self.source_columns) < 2:
            QMessageBox.warning(
                self, 
                'Invalid Selection', 
                'Please select at least two source columns.'
            )
            return
        
        super().accept()

class RenameColumnDialog(QDialog):
    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Rename Column')
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Current name display
        current_layout = QHBoxLayout()
        current_label = QLabel('Current Name:')
        current_name_display = QLabel(current_name)
        current_layout.addWidget(current_label)
        current_layout.addWidget(current_name_display)
        layout.addLayout(current_layout)
        
        # New name input
        new_name_layout = QHBoxLayout()
        new_name_label = QLabel('New Name:')
        self.new_name_input = QLineEdit(current_name)
        new_name_layout.addWidget(new_name_label)
        new_name_layout.addWidget(self.new_name_input)
        layout.addLayout(new_name_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Property to store new name
        self.new_name = current_name
    
    def accept(self):
        # Validate and store new name
        self.new_name = self.new_name_input.text().strip()
        
        # Ensure new name is not empty
        if not self.new_name:
            QMessageBox.warning(
                self, 
                'Invalid Name', 
                'New column name cannot be empty.'
            )
            return
        
        super().accept()

class MappingUI(QWidget):
    def __init__(self, parent=None, df=None, pete_headers=None, rules=None, on_back=None, on_exit=None, on_settings=None):
        super().__init__(parent)
        self.df = df
        self.pete_headers = pete_headers
        self.rules = rules or {}
        self.on_back = on_back
        self.on_exit = on_exit
        self.on_settings = on_settings
        self.standardizer = DataStandardizer(pete_headers)
        self.standardizer.rules = self.rules
        self.mapping = self.standardizer.propose_mapping(list(df.columns))
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(create_logo_label())
        
        header_layout = QHBoxLayout()
        self.toggle_btn = QPushButton('Show Upload Headers')
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self.toggle_headers)
        header_layout.addWidget(QLabel('Mapping UI'))
        header_layout.addWidget(self.toggle_btn)
        
        if self.on_settings:
            gear_btn = QToolButton()
            gear_btn.setIcon(QIcon.fromTheme('preferences-system') or QIcon('settings.png'))
            gear_btn.setToolTip('Settings')
            gear_btn.clicked.connect(self.on_settings)
            header_layout.addWidget(gear_btn)
        
        # Add rule editing button
        self.edit_rules_btn = QPushButton('Edit Mapping Rules')
        self.edit_rules_btn.clicked.connect(self.edit_mapping_rules)
        header_layout.addWidget(self.edit_rules_btn)
        
        self.layout.addLayout(header_layout)
        
        # Use MappingTableWidget instead of standard QTableWidget
        self.mapping_table = MappingTableWidget()
        self.mapping_table.setSelectionMode(QAbstractItemView.ExtendedSelection)  # Allow multi-select
        self.mapping_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mapping_table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.layout.addWidget(self.mapping_table)
        
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton('Back to Main Menu')
        self.exit_btn = QPushButton('Exit')
        self.back_btn.clicked.connect(self.handle_back)
        self.exit_btn.clicked.connect(self.handle_exit)
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.exit_btn)
        self.layout.addLayout(nav_layout)
    
    def show_context_menu(self, pos):
        """Show context menu for selected columns."""
        context_menu = QMenu(self)
        
        # Get selected columns
        selected_columns = set(index.column() for index in self.mapping_table.selectedIndexes())
        
        # Concatenate action
        if len(selected_columns) > 1:
            concat_action = QAction('Concatenate Columns', self)
            concat_action.triggered.connect(lambda: self.concatenate_selected_columns(list(selected_columns)))
            context_menu.addAction(concat_action)
        
        # Rename column action
        if len(selected_columns) == 1:
            rename_action = QAction('Rename Column', self)
            rename_action.triggered.connect(lambda: self.rename_column(list(selected_columns)[0]))
            context_menu.addAction(rename_action)
        
        context_menu.exec_(self.mapping_table.mapToGlobal(pos))
    
    def update_mapping_table(self):
        show_upload = self.toggle_btn.isChecked()
        
        # Clear existing table
        self.mapping_table.clear()
        self.mapping_table.setRowCount(0)
        self.mapping_table.setColumnCount(0)
        
        if show_upload:
            # Show upload columns as rows, map to Pete headers
            columns = ['Upload Column', 'Mapped Pete Header', 'Rule/Reason']
            self.mapping_table.setColumnCount(len(columns))
            self.mapping_table.setHorizontalHeaderLabels(columns)
            
            data = []
            for col in self.df.columns:
                mapping = next(((pete, reason) for c, (pete, _, reason) in self.mapping.items() if c == col), (None, ''))
                data.append([col, mapping[0] or '', mapping[1]])
            
            self.mapping_table.setRowCount(len(data))
            for row_idx, row in enumerate(data):
                for col_idx, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    self.mapping_table.setItem(row_idx, col_idx, item)
                
                # Add dropdown for mapping
                combo = QComboBox()
                combo.addItem('')
                for pete in self.pete_headers:
                    combo.addItem(pete)
                current_pete = self.mapping.get(self.df.columns[row_idx], (None,))[0]
                if current_pete:
                    combo.setCurrentText(current_pete)
                combo.currentTextChanged.connect(lambda val, c=self.df.columns[row_idx]: self.update_mapping_from_upload(c, val))
                self.mapping_table.setCellWidget(row_idx, 1, combo)
        
        else:
            # Show Pete headers as rows, map to upload columns
            columns = ['Pete Header', 'Mapped Upload Column', 'Rule/Reason']
            self.mapping_table.setColumnCount(len(columns))
            self.mapping_table.setHorizontalHeaderLabels(columns)
            
            reverse_map = {}
            for col, (pete, _, reason) in self.mapping.items():
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
                
                # Add dropdown for mapping
                combo = QComboBox()
                combo.addItem('')
                for col in self.df.columns:
                    combo.addItem(col)
                
                # Find which upload col is mapped to this Pete header
                mapped_col = ''
                for c, (p, _, _) in self.mapping.items():
                    if p == pete:
                        mapped_col = c
                        break
                
                if mapped_col:
                    combo.setCurrentText(mapped_col)
                
                combo.currentTextChanged.connect(lambda val, p=pete: self.update_mapping_from_pete(p, val))
                self.mapping_table.setCellWidget(row_idx, 1, combo)
        
        self.mapping_table.resizeColumnsToContents()

    def update_mapping_from_upload(self, col, pete):
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

    def update_mapping_from_pete(self, pete, col):
        # Enforce one-to-one mapping
        for c in self.mapping:
            if self.mapping[c][0] == pete and c != col and pete:
                self.mapping[c] = (None, 0.0, 'Unmapped (duplicate)')
        # Find which col is currently mapped to this Pete header
        for c in self.mapping:
            if self.mapping[c][0] == pete:
                self.mapping[c] = (None, 0.0, 'Manual skip')
        if col:
            self.mapping[col] = (pete, 100.0, 'Manual')
        self.update_mapping_table()

    def toggle_headers(self):
        if self.toggle_btn.isChecked():
            self.toggle_btn.setText('Show Pete Headers')
        else:
            self.toggle_btn.setText('Show Upload Headers')
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
            self.rules = rule_dialog.current_rules
            
            # Rerun mapping with new rules
            self.standardizer.rules = self.rules
            self.mapping = self.standardizer.propose_mapping(list(self.df.columns))
            
            # Update mapping table
            self.update_mapping_table()

    def start_concatenation(self, initial_column, is_pete_header=False):
        """Open concatenation dialog and update mapping."""
        # Determine available columns based on context
        if is_pete_header:
            # If starting from a Pete header, find its current mapping
            initial_column = next(
                (col for col, (mapped_pete, _, _) in self.mapping.items() if mapped_pete == initial_column), 
                None
            )
            if not initial_column:
                QMessageBox.warning(self, 'No Mapping', f'No column currently mapped to {initial_column}')
                return
            available_columns = list(self.df.columns)
        else:
            # If starting from an upload column, use all columns except the initial one
            available_columns = [col for col in self.df.columns if col != initial_column]
        
        # Open concatenation dialog
        concat_dialog = ConcatenationDialog(
            upload_columns=available_columns, 
            pete_headers=self.pete_headers, 
            parent=self
        )
        
        if concat_dialog.exec_() == QDialog.Accepted and concat_dialog.result:
            result = concat_dialog.result
            
            # Update rules
            concat_fields = self.rules.get('concat_fields', {})
            concat_fields[result['destination_header']] = result['source_columns']
            self.rules['concat_fields'] = concat_fields
            self.rules['concat_separator'] = result['separator']
            
            # Rerun mapping with updated rules
            self.standardizer.rules = self.rules
            self.mapping = self.standardizer.propose_mapping(list(self.df.columns))
            
            # Update mapping table
            self.update_mapping_table()
            
            # Optional: Show confirmation
            QMessageBox.information(
                self, 
                'Concatenation Added', 
                f"Concatenated {' + '.join(result['source_columns'])} to {result['destination_header']}"
            )

    def concatenate_selected_columns(self, columns):
        """Concatenate selected columns."""
        # Get column names for selected columns
        column_names = [self.df.columns[col] for col in columns]
        
        # Open concatenation dialog with pre-selected columns
        concat_dialog = ConcatenationDialog(
            upload_columns=self.df.columns, 
            pete_headers=self.pete_headers, 
            pre_selected_columns=column_names,
            parent=self
        )
        
        if concat_dialog.exec_() == QDialog.Accepted and concat_dialog.result:
            result = concat_dialog.result
            
            # Update rules
            concat_fields = self.rules.get('concat_fields', {})
            concat_fields[result['destination_header']] = result['source_columns']
            self.rules['concat_fields'] = concat_fields
            self.rules['concat_separator'] = result['separator']
            
            # Rerun mapping with updated rules
            self.standardizer.rules = self.rules
            self.mapping = self.standardizer.propose_mapping(list(self.df.columns))
            
            # Update mapping table
            self.update_mapping_table()
            
            # Optional: Show confirmation
            QMessageBox.information(
                self, 
                'Concatenation Added', 
                f"Concatenated {' + '.join(result['source_columns'])} to {result['destination_header']}"
            )
    
    def rename_column(self, column_index):
        """Rename a specific column."""
        current_column_name = self.df.columns[column_index]
        new_name, ok = QInputDialog.getText(
            self, 
            'Rename Column', 
            f'Enter new name for column "{current_column_name}":',
            QLineEdit.Normal, 
            current_column_name
        )
        
        if ok and new_name:
            # Rename the column in the DataFrame
            self.df.rename(columns={current_column_name: new_name}, inplace=True)
            
            # Rerun mapping
            self.mapping = self.standardizer.propose_mapping(list(self.df.columns))
            
            # Update mapping table
            self.update_mapping_table()

    def handle_back(self):
        if self.on_back:
            self.on_back()
    def handle_exit(self):
        if self.on_exit:
            self.on_exit()

    def concatenate_columns(self, source_columns, destination_column, separator):
        """
        Concatenate selected columns and map to a destination column.
        
        :param source_columns: List of column names to concatenate
        :param destination_column: Column to map the concatenated result to
        :param separator: String to use between concatenated values
        """
        try:
            # Validate inputs
            if len(source_columns) < 2:
                QMessageBox.warning(
                    self, 
                    'Concatenation Error', 
                    'Select at least two columns to concatenate.'
                )
                return

            # Create concatenated column
            concat_series = self.df[source_columns].apply(
                lambda row: separator.join(str(val) for val in row if pd.notna(val)), 
                axis=1
            )

            # Update DataFrame
            self.df[destination_column] = concat_series

            # Update mapping rules
            if 'concat_fields' not in self.rules:
                self.rules['concat_fields'] = {}
            
            # Store concatenation rule
            self.rules['concat_fields'][destination_column] = source_columns
            self.rules['concat_separator'] = separator

            # Refresh mapping
            self.update_mapping_table()

            # Notify user
            QMessageBox.information(
                self, 
                'Concatenation Successful', 
                f'Columns {", ".join(source_columns)} concatenated to {destination_column}'
            )

        except Exception as e:
            QMessageBox.critical(
                self, 
                'Concatenation Error', 
                f'Failed to concatenate columns: {str(e)}'
            )

    def rename_column(self, old_name, new_name):
        """
        Rename a column in the DataFrame and update mapping.
        
        :param old_name: Current column name
        :param new_name: New column name
        """
        try:
            # Validate new name
            if new_name in self.df.columns:
                QMessageBox.warning(
                    self, 
                    'Rename Error', 
                    f'Column {new_name} already exists.'
                )
                return

            # Rename column
            self.df.rename(columns={old_name: new_name}, inplace=True)

            # Update any existing mappings
            if old_name in self.mapping:
                mapping_info = self.mapping[old_name]
                del self.mapping[old_name]
                self.mapping[new_name] = mapping_info

            # Refresh mapping table
            self.update_mapping_table()

            # Notify user
            QMessageBox.information(
                self, 
                'Column Renamed', 
                f'Column {old_name} renamed to {new_name}'
            )

        except Exception as e:
            QMessageBox.critical(
                self, 
                'Rename Error', 
                f'Failed to rename column: {str(e)}'
            )

class StandardizedPreviewUI(QWidget):
    def __init__(self, parent=None, df=None, on_back=None, on_exit=None):
        super().__init__(parent)
        self.df = df
        self.on_back = on_back
        self.on_exit = on_exit
        self.init_ui()
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(create_logo_label())
        self.label = QLabel('Standardized Data Preview')
        self.layout.addWidget(self.label)
        self.table_widget = QTableWidget()
        preview_rows = min(rules_config.get('preview_row_count', 10), len(self.df))
        preview_cols = len(self.df.columns)
        self.table_widget.setRowCount(preview_rows)
        self.table_widget.setColumnCount(preview_cols)
        self.table_widget.setHorizontalHeaderLabels([str(col) for col in self.df.columns])
        for i in range(preview_rows):
            for j in range(preview_cols):
                val = str(self.df.iloc[i, j]) if j < len(self.df.columns) else ''
                self.table_widget.setItem(i, j, QTableWidgetItem(val))
        self.table_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_widget.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.layout.addWidget(self.table_widget)
        btn_layout = QHBoxLayout()
        self.download_csv_btn = QPushButton('Download as CSV')
        self.download_xlsx_btn = QPushButton('Download as XLSX')
        self.back_btn = QPushButton('Back to Main Menu')
        self.exit_btn = QPushButton('Exit')
        btn_layout.addWidget(self.download_csv_btn)
        btn_layout.addWidget(self.download_xlsx_btn)
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.exit_btn)
        self.layout.addLayout(btn_layout)
        self.download_csv_btn.clicked.connect(self.download_csv)
        self.download_xlsx_btn.clicked.connect(self.download_xlsx)
        self.back_btn.clicked.connect(self.handle_back)
        self.exit_btn.clicked.connect(self.handle_exit)
    def download_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save CSV', '', 'CSV Files (*.csv)')
        if path:
            self.df.to_csv(path, index=False)
            QMessageBox.information(self, 'Saved', f'Standardized data saved as CSV to {path}')
    def download_xlsx(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Save XLSX', '', 'Excel Files (*.xlsx)')
        if path:
            self.df.to_excel(path, index=False)
            QMessageBox.information(self, 'Saved', f'Standardized data saved as XLSX to {path}')
    def handle_back(self):
        if self.on_back:
            self.on_back()
    def handle_exit(self):
        if self.on_exit:
            self.on_exit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pete GUI Mapping Tool (PyQt5)')
        self.resize(1100, 700)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.layout.addWidget(create_logo_label())
        self.menu_options = {
            'Workspace': ("Workspace", True),
            'Standardize': ("Standardize", True),
            'Rules': ("Rules", True),
            'Backend': ("Backend", True),
            'Test': ("Test", True),
            'GUI Mapping Tool': ("GUI Mapping Tool", True),
            'Exit': ("Exit", True)
        }
        self.settings_btn = QToolButton()
        self.settings_btn.setIcon(QIcon.fromTheme('preferences-system') or QIcon('settings.png'))
        self.settings_btn.setToolTip('Settings')
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setStyleSheet('QToolButton { float: right; }')
        self.layout.addWidget(self.settings_btn, alignment=Qt.AlignRight)
        self.show_startup_menu()
    def show_startup_menu(self):
        self.clear_layout(keep_settings=True)
        visible_options = [(k, v[0]) for k, v in self.menu_options.items() if v[1]]
        self.menu = StartupMenu(self, on_select=self.handle_menu_select, options=visible_options)
        self.layout.addWidget(self.menu)
    def show_file_selector(self):
        self.clear_layout(keep_settings=True)
        self.file_selector = FileSelector(self, on_exit=self.show_startup_menu)
        self.layout.addWidget(self.file_selector)
    def show_mapping_ui(self, df, pete_headers):
        self.clear_layout(keep_settings=True)
        self.mapping_ui = MappingUI(self, df=df, pete_headers=pete_headers, rules=rules_config,
                                    on_back=self.show_startup_menu, on_exit=self.close, on_settings=self.open_settings)
        self.layout.addWidget(self.mapping_ui)
    def show_standardized_preview(self, df):
        self.clear_layout(keep_settings=True)
        self.std_preview = StandardizedPreviewUI(self, df=df, on_back=self.show_startup_menu, on_exit=self.close)
        self.layout.addWidget(self.std_preview)
    def handle_menu_select(self, name):
        if name == "GUI Mapping Tool":
            self.show_file_selector()
        elif name == "Exit":
            self.close()
        else:
            QMessageBox.information(self, name, f"{name} utility coming soon.")
            self.show_startup_menu()
    def clear_layout(self, keep_settings=False):
        widgets = []
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if item.widget() is not None:
                widgets.append(item.widget())
        for w in widgets:
            if keep_settings and w == self.settings_btn:
                continue
            self.layout.removeWidget(w)
            w.deleteLater()
    def open_settings(self):
        dlg = SettingsDialog(self, rules=rules_config, menu_options=self.menu_options, on_save=self.apply_settings)
        dlg.exec_()
    def apply_settings(self, new_rules, new_menu_options):
        rules_config.update(new_rules)
        self.menu_options.update(new_menu_options)
        logger.info(f"Settings updated: {rules_config}, Menu: {self.menu_options}")
        # Live update: re-show current screen with new settings
        self.show_startup_menu()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 