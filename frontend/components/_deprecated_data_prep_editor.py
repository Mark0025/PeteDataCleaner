"""
Data Preparation Editor Component

Smart editor for preparing upload data before Pete mapping.
Features column editing, concatenation, and version history.
"""

import pandas as pd
import copy
import json
import os
from typing import Dict, List, Any, Optional, Callable, Tuple
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu, QAction,
    QDialog, QDialogButtonBox, QListWidget, QComboBox, QCheckBox,
    QMessageBox, QInputDialog, QGroupBox, QSplitter, QTextEdit,
    QScrollArea, QFrame
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from frontend.components.base_component import BaseComponent
from frontend.dialogs.concatenation_dialog import ConcatenationDialog

class DataVersionManager:
    """Manages version history for data preparation changes."""
    
    def __init__(self):
        self.versions: List[Dict[str, Any]] = []
        self.current_version = -1
    
    def save_version(self, df: pd.DataFrame, action: str, details: str = ""):
        """Save a new version of the data."""
        version_info = {
            'data': df.copy(),
            'action': action,
            'details': details,
            'timestamp': pd.Timestamp.now().strftime('%H:%M:%S'),
            'columns': list(df.columns),
            'rows': len(df),
            'version_number': len(self.versions) + 1
        }
        
        # If we're not at the latest version, remove future versions
        if self.current_version < len(self.versions) - 1:
            self.versions = self.versions[:self.current_version + 1]
        
        self.versions.append(version_info)
        self.current_version = len(self.versions) - 1
        
        return version_info['version_number']
    
    def get_current_data(self) -> Optional[pd.DataFrame]:
        """Get current version of data."""
        if self.current_version >= 0:
            return self.versions[self.current_version]['data'].copy()
        return None
    
    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return self.current_version > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return self.current_version < len(self.versions) - 1
    
    def undo(self) -> Optional[pd.DataFrame]:
        """Undo to previous version."""
        if self.can_undo():
            self.current_version -= 1
            return self.get_current_data()
        return None
    
    def redo(self) -> Optional[pd.DataFrame]:
        """Redo to next version."""
        if self.can_redo():
            self.current_version += 1
            return self.get_current_data()
        return None
    
    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get version history for display."""
        return [
            {
                'version': v['version_number'],
                'action': v['action'],
                'details': v['details'],
                'timestamp': v['timestamp'],
                'columns': len(v['columns']),
                'rows': v['rows'],
                'is_current': i == self.current_version
            }
            for i, v in enumerate(self.versions)
        ]

class SmartConcatenationDialog(QDialog):
    """Enhanced concatenation dialog with delimiter options and column management."""
    
    DELIMITERS = {
        'Space': ' ',
        'Comma + Space': ', ',
        'Semicolon + Space': '; ',
        'Pipe + Space': ' | ',
        'Newline': '\n',
        'Comma': ',',
        'Dash': ' - ',
        'Underscore': '_',
        'Pipe': '|',
        'Custom': ''
    }
    
    def __init__(self, selected_columns: List[str], all_columns: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle('Smart Column Merger')
        self.setModal(True)
        self.resize(500, 400)
        
        self.selected_columns = selected_columns
        self.all_columns = all_columns
        self.result = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f'🔗 Smart Column Merger ({len(self.selected_columns)} columns)')
        title.setStyleSheet('font-size: 16px; font-weight: bold; color: #1976d2; margin-bottom: 10px;')
        layout.addWidget(title)
        
        # Selected columns display
        selected_group = QGroupBox('Selected Columns to Merge')
        selected_layout = QVBoxLayout(selected_group)
        
        self.columns_list = QListWidget()
        for col in self.selected_columns:
            self.columns_list.addItem(f"📋 {col}")
        self.columns_list.setMaximumHeight(100)
        selected_layout.addWidget(self.columns_list)
        layout.addWidget(selected_group)
        
        # Delimiter selection
        delimiter_group = QGroupBox('Choose Delimiter')
        delimiter_layout = QVBoxLayout(delimiter_group)
        
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems(list(self.DELIMITERS.keys()))
        self.delimiter_combo.setCurrentText('Space')
        self.delimiter_combo.currentTextChanged.connect(self._on_delimiter_changed)
        delimiter_layout.addWidget(self.delimiter_combo)
        
        # Custom delimiter input
        self.custom_delimiter = QInputDialog()
        
        delimiter_layout.addWidget(QLabel('Preview: "John" + "Doe" → "John Doe"'))
        layout.addWidget(delimiter_group)
        
        # New column name
        name_group = QGroupBox('New Column Name')
        name_layout = QVBoxLayout(name_group)
        
        self.new_name_input = QComboBox()
        self.new_name_input.setEditable(True)
        
        # Suggest smart names
        smart_names = self._generate_smart_names()
        self.new_name_input.addItems(smart_names)
        self.new_name_input.setCurrentText(smart_names[0] if smart_names else 'Merged_Column')
        
        name_layout.addWidget(self.new_name_input)
        layout.addWidget(name_group)
        
        # Options
        options_group = QGroupBox('Options')
        options_layout = QVBoxLayout(options_group)
        
        self.keep_original = QCheckBox('Keep original columns after merging')
        self.keep_original.setChecked(False)
        self.keep_original.setToolTip('If unchecked, original columns will be removed')
        options_layout.addWidget(self.keep_original)
        
        self.handle_empty = QCheckBox('Skip empty values when merging')
        self.handle_empty.setChecked(True)
        self.handle_empty.setToolTip('Empty/NaN values will be ignored in concatenation')
        options_layout.addWidget(self.handle_empty)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _generate_smart_names(self) -> List[str]:
        """Generate smart suggestions for merged column names."""
        suggestions = []
        
        if len(self.selected_columns) == 2:
            col1, col2 = self.selected_columns
            
            # Full name patterns
            if any(word in col1.lower() for word in ['first', 'fname', 'given']) and \
               any(word in col2.lower() for word in ['last', 'lname', 'surname', 'family']):
                suggestions.append('Full Name')
                suggestions.append('Seller')  # Pete-specific
            
            # Address patterns  
            if any(word in col1.lower() for word in ['street', 'address']) and \
               any(word in col2.lower() for word in ['city', 'town']):
                suggestions.append('Full Address')
            
            # Email patterns
            if 'email' in col1.lower() and 'email' in col2.lower():
                suggestions.append('Combined Email')
            
            # Phone patterns
            if 'phone' in col1.lower() and 'phone' in col2.lower():
                suggestions.append('Combined Phone')
            
            # Generic combination
            suggestions.append(f"{col1}_{col2}")
            suggestions.append(f"Combined_{col1.split()[0] if col1.split() else col1}")
        
        elif len(self.selected_columns) >= 3:
            # Multiple columns - enhanced suggestions for "Notes" use case
            col_names_lower = [col.lower() for col in self.selected_columns]
            
            # Check if these look like miscellaneous/notes fields
            notes_keywords = ['note', 'comment', 'remark', 'desc', 'detail', 'misc', 'other', 'additional']
            if any(keyword in ' '.join(col_names_lower) for keyword in notes_keywords):
                suggestions.extend([
                    'Notes',
                    'Additional Notes', 
                    'Combined Notes',
                    'Misc Information'
                ])
            
            # Check if these are contact fields
            contact_keywords = ['email', 'phone', 'contact', 'call', 'text']
            if any(keyword in ' '.join(col_names_lower) for keyword in contact_keywords):
                suggestions.extend([
                    'Contact Information',
                    'All Contact Details',
                    'Combined Contacts'
                ])
            
            # Check if these are address-related
            address_keywords = ['street', 'address', 'city', 'state', 'zip', 'county']
            if any(keyword in ' '.join(col_names_lower) for keyword in address_keywords):
                suggestions.extend([
                    'Full Address',
                    'Complete Address',
                    'Property Address Details'
                ])
            
            # Always include these versatile options
            suggestions.extend([
                'Notes',  # Most common use case
                'Additional Information',
                'Combined Details',
                'Merged Data',
                f"Combined_{len(self.selected_columns)}_Fields",
                'Miscellaneous'
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions or ['Merged_Column']
    
    def _on_delimiter_changed(self, delimiter_name: str):
        """Handle delimiter selection change."""
        if delimiter_name == 'Custom':
            text, ok = QInputDialog.getText(
                self, 
                'Custom Delimiter', 
                'Enter custom delimiter:'
            )
            if ok:
                self.custom_delimiter_text = text
            else:
                self.delimiter_combo.setCurrentText('Space')
    
    def _validate_and_accept(self):
        """Validate inputs and prepare result."""
        new_name = self.new_name_input.currentText().strip()
        if not new_name:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a name for the new column.')
            return
        
        if new_name in self.all_columns:
            reply = QMessageBox.question(
                self,
                'Column Exists',
                f'Column "{new_name}" already exists. Do you want to replace it?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Get delimiter
        delimiter_name = self.delimiter_combo.currentText()
        if delimiter_name == 'Custom':
            delimiter = getattr(self, 'custom_delimiter_text', ' ')
        else:
            delimiter = self.DELIMITERS[delimiter_name]
        
        self.result = {
            'columns': self.selected_columns,
            'new_name': new_name,
            'delimiter': delimiter,
            'keep_original': self.keep_original.isChecked(),
            'handle_empty': self.handle_empty.isChecked()
        }
        
        self.accept()

class DataPrepEditor(BaseComponent):
    """
    Smart data preparation editor component.
    
    Features:
    - Interactive column editing
    - Smart concatenation with multiple delimiters
    - Version history with undo/redo
    - Clean data preview
    - State management
    """
    
    # Signals for communication with parent
    data_ready_for_mapping = pyqtSignal(pd.DataFrame)
    
    def __init__(self, parent=None, df: Optional[pd.DataFrame] = None,
                 on_back: Optional[Callable] = None, 
                 on_proceed: Optional[Callable] = None):
        """
        Initialize data preparation editor.
        
        Args:
            parent: Parent widget
            df: Initial DataFrame to edit
            on_back: Callback for back button
            on_proceed: Callback when data is ready for Pete mapping
        """
        super().__init__(parent, show_logo=True, show_navigation=True,
                         on_back=on_back, on_exit=None)
        
        if df is None:
            raise ValueError("DataFrame is required for data preparation")
        
        self.original_df = df.copy()
        self.on_proceed = on_proceed
        
        # Version management
        self.version_manager = DataVersionManager()
        self.version_manager.save_version(df, "Initial Upload", "Original data loaded")
        
        # UI state
        self.selected_columns = []
        self.hidden_columns = set()  # Track hidden columns
        self.never_map_rules = self._load_never_map_rules()
        
        self._setup_ui()
        self._refresh_data_view()
    
    def _load_never_map_rules(self) -> List[str]:
        """Load never map rules from mapping_rules.json"""
        try:
            rules_path = os.path.join("DEV_MAN", "mappings", "mapping_rules.json")
            if os.path.exists(rules_path):
                with open(rules_path, 'r') as f:
                    rules = json.load(f)
                    return rules.get('never_map', [])
        except Exception as e:
            print(f"Warning: Could not load never map rules: {e}")
        return []
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Title and stats
        title_layout = QHBoxLayout()
        
        title = QLabel('📝 Data Preparation Editor')
        title.setStyleSheet('font-size: 18px; font-weight: bold; color: #1976d2;')
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet('color: #666; font-size: 12px;')
        title_layout.addWidget(self.stats_label)
        
        self.layout.addLayout(title_layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Data table
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        # Data table controls
        table_controls = QHBoxLayout()
        
        self.merge_btn = QPushButton('🔗 Merge Selected Columns')
        self.merge_btn.setEnabled(False)
        self.merge_btn.clicked.connect(self._merge_columns)
        self.merge_btn.setToolTip('Select 2 or more columns to merge them into a single column')
        self.merge_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        table_controls.addWidget(self.merge_btn)
        
        self.rename_btn = QPushButton('✏️ Rename Column')
        self.rename_btn.setEnabled(False)
        self.rename_btn.clicked.connect(self._rename_column)
        table_controls.addWidget(self.rename_btn)
        
        table_controls.addStretch()
        
        # Version controls
        self.undo_btn = QPushButton('↶ Undo')
        self.undo_btn.setEnabled(False)
        self.undo_btn.clicked.connect(self._undo)
        table_controls.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton('↷ Redo')
        self.redo_btn.setEnabled(False)
        self.redo_btn.clicked.connect(self._redo)
        table_controls.addWidget(self.redo_btn)
        
        left_layout.addLayout(table_controls)
        
        # Column visibility controls
        visibility_controls = QHBoxLayout()
        
        self.hide_btn = QPushButton('👁️‍🗨️ Hide Selected')
        self.hide_btn.setEnabled(False)
        self.hide_btn.clicked.connect(self._hide_selected_columns)
        self.hide_btn.setToolTip('Hide selected columns from view')
        visibility_controls.addWidget(self.hide_btn)
        
        self.show_hidden_btn = QPushButton('👁️ Show Hidden')
        self.show_hidden_btn.clicked.connect(self._show_hidden_columns)
        self.show_hidden_btn.setToolTip('Show all hidden columns')
        visibility_controls.addWidget(self.show_hidden_btn)
        
        self.hide_never_map_btn = QPushButton('🚫 Hide Never-Map Fields')
        self.hide_never_map_btn.clicked.connect(self._hide_never_map_columns)
        self.hide_never_map_btn.setToolTip('Hide columns that will never be mapped to Pete')
        visibility_controls.addWidget(self.hide_never_map_btn)
        
        visibility_controls.addStretch()
        
        # Hidden columns indicator
        self.hidden_indicator = QLabel()
        self.hidden_indicator.setStyleSheet('color: #666; font-style: italic;')
        visibility_controls.addWidget(self.hidden_indicator)
        
        left_layout.addLayout(visibility_controls)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.data_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.data_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.data_table.customContextMenuRequested.connect(self._show_context_menu)
        self.data_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Style the table for better readability
        self.data_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        left_layout.addWidget(self.data_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        self.reset_btn = QPushButton('🔄 Reset to Original')
        self.reset_btn.clicked.connect(self._reset_to_original)
        action_layout.addWidget(self.reset_btn)
        
        self.proceed_btn = QPushButton('➡️ Proceed to Pete Mapping')
        self.proceed_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.proceed_btn.clicked.connect(self._proceed_to_mapping)
        action_layout.addWidget(self.proceed_btn)
        
        left_layout.addLayout(action_layout)
        
        # Right panel - Version history and info
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        # Version history
        history_label = QLabel('📚 Version History')
        history_label.setStyleSheet('font-weight: bold; font-size: 14px; margin-bottom: 5px;')
        right_layout.addWidget(history_label)
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(200)
        right_layout.addWidget(self.history_list)
        
        # Column info
        info_label = QLabel('ℹ️ Column Information')
        info_label.setStyleSheet('font-weight: bold; font-size: 14px; margin: 10px 0 5px 0;')
        right_layout.addWidget(info_label)
        
        self.column_info = QTextEdit()
        self.column_info.setMaximumHeight(150)
        self.column_info.setReadOnly(True)
        right_layout.addWidget(self.column_info)
        
        right_layout.addStretch()
        
        # Set panel sizes
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 300])  # 800px for table, 300px for sidebar
        
        self.layout.addWidget(splitter)
    
    def _refresh_data_view(self):
        """Refresh the data table view with current data."""
        current_df = self.version_manager.get_current_data()
        if current_df is None:
            return
        
        # Filter out hidden columns
        visible_columns = [col for col in current_df.columns if col not in self.hidden_columns]
        display_df = current_df[visible_columns] if visible_columns else current_df
        
        # Update stats
        hidden_count = len(self.hidden_columns)
        total_cols = len(current_df.columns)
        visible_cols = len(visible_columns)
        
        self.stats_label.setText(
            f"📊 {len(current_df)} rows × {visible_cols}/{total_cols} columns" +
            (f" ({hidden_count} hidden)" if hidden_count > 0 else "")
        )
        
        # Update hidden columns indicator
        if hidden_count > 0:
            never_map_hidden = sum(1 for col in self.hidden_columns if col in self.never_map_rules)
            self.hidden_indicator.setText(
                f"Hidden: {hidden_count} columns" +
                (f" ({never_map_hidden} never-map)" if never_map_hidden > 0 else "")
            )
        else:
            self.hidden_indicator.setText("")
        
        # Update table
        self.data_table.clear()
        self.data_table.setRowCount(min(20, len(display_df)))  # Show first 20 rows
        self.data_table.setColumnCount(len(visible_columns))
        
        # Set headers with better formatting and never-map indicators
        headers = []
        for col in visible_columns:
            # Truncate long column names for display
            display_name = col if len(col) <= 20 else col[:17] + "..."
            
            # Mark never-map columns
            if col in self.never_map_rules:
                display_name = f"🚫 {display_name}"
                
            headers.append(display_name)
        
        self.data_table.setHorizontalHeaderLabels(headers)
        
        # Populate data (only visible columns)
        for i in range(min(20, len(display_df))):
            for j, col in enumerate(visible_columns):
                value = str(display_df.iloc[i, j]) if pd.notna(display_df.iloc[i, j]) else ""
                item = QTableWidgetItem(value)
                
                # Enhanced tooltip with never-map indication
                tooltip = f"Column: {col}\nRow: {i+1}\nValue: {value}"
                if col in self.never_map_rules:
                    tooltip += "\n🚫 This column will never be mapped to Pete"
                item.setToolTip(tooltip)
                
                self.data_table.setItem(i, j, item)
        
        # Auto-resize columns for better visibility
        self.data_table.resizeColumnsToContents()
        
        # Update version controls
        self._update_version_controls()
        self._update_version_history()
    
    def _update_version_controls(self):
        """Update undo/redo button states."""
        self.undo_btn.setEnabled(self.version_manager.can_undo())
        self.redo_btn.setEnabled(self.version_manager.can_redo())
    
    def _update_version_history(self):
        """Update version history display."""
        self.history_list.clear()
        
        for version_info in reversed(self.version_manager.get_version_history()):
            prefix = "→ " if version_info['is_current'] else "  "
            text = f"{prefix}v{version_info['version']} [{version_info['timestamp']}] {version_info['action']}"
            if version_info['details']:
                text += f" - {version_info['details']}"
            
            item = self.history_list.addItem(text)
            if version_info['is_current']:
                font = self.history_list.font()
                font.setBold(True)
                self.history_list.item(self.history_list.count() - 1).setFont(font)
    
    def _on_selection_changed(self):
        """Handle table selection changes."""
        selected_ranges = self.data_table.selectedRanges()
        self.selected_columns = []
        
        # Get selected column names (from visible columns only)
        current_df = self.version_manager.get_current_data()
        if current_df is not None:
            visible_columns = [col for col in current_df.columns if col not in self.hidden_columns]
            
            for range_item in selected_ranges:
                for col_idx in range(range_item.leftColumn(), range_item.rightColumn() + 1):
                    if col_idx < len(visible_columns):
                        col_name = visible_columns[col_idx]
                        if col_name not in self.selected_columns:
                            self.selected_columns.append(col_name)
        
        # Update button states
        self.merge_btn.setEnabled(len(self.selected_columns) >= 2)
        self.rename_btn.setEnabled(len(self.selected_columns) == 1)
        self.hide_btn.setEnabled(len(self.selected_columns) > 0)
        
        # Update column info
        self._update_column_info()
    
    def _update_column_info(self):
        """Update column information display."""
        if not self.selected_columns:
            self.column_info.setText("Select columns to see details and merge options.\n\n💡 Tip: Select 2+ columns to merge them into 'Notes' or other combined fields!")
            return
        
        current_df = self.version_manager.get_current_data()
        if current_df is None:
            return
        
        # Show merge suggestion based on selection count
        if len(self.selected_columns) >= 3:
            merge_hint = f"\n💡 Perfect for creating a 'Notes' field from {len(self.selected_columns)} columns!"
        elif len(self.selected_columns) == 2:
            merge_hint = f"\n💡 Great for combining related fields like 'First + Last Name'!"
        else:
            merge_hint = f"\n💡 Select one more column to enable merging!"
        
        info_text = f"Selected {len(self.selected_columns)} column(s):{merge_hint}\n\n"
        
        for col in self.selected_columns:
            if col in current_df.columns:
                series = current_df[col]
                info_text += f"📋 {col}\n"
                info_text += f"  • Type: {series.dtype}\n"
                info_text += f"  • Non-null: {series.notna().sum()}/{len(series)}\n"
                info_text += f"  • Unique: {series.nunique()}\n"
                
                # Sample values
                sample_values = series.dropna().head(3).tolist()
                if sample_values:
                    sample_str = ", ".join(str(v)[:30] for v in sample_values)
                    info_text += f"  • Sample: {sample_str}\n"
                info_text += "\n"
        
        self.column_info.setText(info_text)
    
    def _show_context_menu(self, pos):
        """Show context menu for table operations."""
        if not self.selected_columns:
            return
        
        menu = QMenu(self)
        
        if len(self.selected_columns) >= 2:
            merge_action = QAction('🔗 Merge Selected Columns', self)
            merge_action.triggered.connect(self._merge_columns)
            menu.addAction(merge_action)
        
        if len(self.selected_columns) == 1:
            rename_action = QAction('✏️ Rename Column', self)
            rename_action.triggered.connect(self._rename_column)
            menu.addAction(rename_action)
        
        if len(self.selected_columns) > 0:
            menu.addSeparator()
            hide_action = QAction('👁️‍🗨️ Hide Selected Columns', self)
            hide_action.triggered.connect(self._hide_selected_columns)
            menu.addAction(hide_action)
            
            # Check if any selected columns are never-map
            never_map_selected = [col for col in self.selected_columns if col in self.never_map_rules]
            if never_map_selected:
                never_map_action = QAction(f'🚫 Hide {len(never_map_selected)} Never-Map Column(s)', self)
                never_map_action.triggered.connect(lambda: self._hide_specific_columns(never_map_selected))
                menu.addAction(never_map_action)
        
        if menu.actions():
            menu.exec_(self.data_table.mapToGlobal(pos))
    
    def _merge_columns(self):
        """Open smart concatenation dialog."""
        current_df = self.version_manager.get_current_data()
        if current_df is None or len(self.selected_columns) < 2:
            return
        
        dialog = SmartConcatenationDialog(
            selected_columns=self.selected_columns,
            all_columns=list(current_df.columns),
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted and dialog.result:
            self._apply_merge(dialog.result)
    
    def _apply_merge(self, merge_config: Dict[str, Any]):
        """Apply the merge operation."""
        current_df = self.version_manager.get_current_data()
        if current_df is None:
            return
        
        try:
            new_df = current_df.copy()
            columns_to_merge = merge_config['columns']
            new_column_name = merge_config['new_name']
            delimiter = merge_config['delimiter']
            handle_empty = merge_config['handle_empty']
            keep_original = merge_config['keep_original']
            
            # Perform concatenation
            if handle_empty:
                # Skip empty values
                new_df[new_column_name] = new_df[columns_to_merge].apply(
                    lambda row: delimiter.join(str(val) for val in row if pd.notna(val) and str(val).strip()),
                    axis=1
                )
            else:
                # Include all values
                new_df[new_column_name] = new_df[columns_to_merge].apply(
                    lambda row: delimiter.join(str(val) if pd.notna(val) else "" for val in row),
                    axis=1
                )
            
            # Remove original columns if requested
            if not keep_original:
                new_df = new_df.drop(columns=columns_to_merge)
            
            # Save version
            action = f"Merged {len(columns_to_merge)} columns"
            details = f"{' + '.join(columns_to_merge)} → {new_column_name}"
            self.version_manager.save_version(new_df, action, details)
            
            # Refresh view
            self._refresh_data_view()
            
            # Show confirmation
            QMessageBox.information(
                self,
                'Merge Complete',
                f'Successfully merged {len(columns_to_merge)} columns into "{new_column_name}"'
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                'Merge Error',
                f'Failed to merge columns: {str(e)}'
            )
    
    def _rename_column(self):
        """Rename a selected column."""
        if len(self.selected_columns) != 1:
            return
        
        current_col = self.selected_columns[0]
        new_name, ok = QInputDialog.getText(
            self,
            'Rename Column',
            f'Enter new name for "{current_col}":',
            text=current_col
        )
        
        if ok and new_name.strip() and new_name != current_col:
            current_df = self.version_manager.get_current_data()
            if current_df is not None:
                try:
                    new_df = current_df.rename(columns={current_col: new_name})
                    
                    # Save version
                    self.version_manager.save_version(
                        new_df, 
                        "Renamed column", 
                        f"{current_col} → {new_name}"
                    )
                    
                    # Refresh view
                    self._refresh_data_view()
                    
                    QMessageBox.information(
                        self,
                        'Rename Complete',
                        f'Column "{current_col}" renamed to "{new_name}"'
                    )
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        'Rename Error',
                        f'Failed to rename column: {str(e)}'
                    )
    
    def _undo(self):
        """Undo last operation."""
        if self.version_manager.undo():
            self._refresh_data_view()
    
    def _redo(self):
        """Redo last undone operation."""
        if self.version_manager.redo():
            self._refresh_data_view()
    
    def _reset_to_original(self):
        """Reset to original uploaded data."""
        reply = QMessageBox.question(
            self,
            'Reset Data',
            'Are you sure you want to reset to the original uploaded data?\nAll changes will be lost.',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.version_manager.save_version(
                self.original_df, 
                "Reset to original", 
                "All changes discarded"
            )
            self._refresh_data_view()
    
    def _proceed_to_mapping(self):
        """Proceed to Pete mapping with prepared data."""
        current_df = self.version_manager.get_current_data()
        if current_df is None:
            return
        
        reply = QMessageBox.question(
            self,
            'Proceed to Mapping',
            f'Ready to map {len(current_df.columns)} columns to Pete headers?\n\n'
            'You can always come back to edit the data if needed.',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Emit signal with prepared data
            self.data_ready_for_mapping.emit(current_df)
            
            # Call callback if provided
            if self.on_proceed:
                self.on_proceed(current_df)
    
    def get_prepared_data(self) -> pd.DataFrame:
        """Get the current prepared data."""
        return self.version_manager.get_current_data()
    
    def _hide_selected_columns(self):
        """Hide the selected columns."""
        if not self.selected_columns:
            return
        
        hidden_count = len(self.selected_columns)
        
        # Add to hidden columns
        for col in self.selected_columns:
            self.hidden_columns.add(col)
        
        # Clear selection
        self.selected_columns = []
        
        # Refresh view
        self._refresh_data_view()
        
        QMessageBox.information(
            self,
            'Columns Hidden',
            f'Hidden {hidden_count} column(s). Use "Show Hidden" to restore them.'
        )
    
    def _show_hidden_columns(self):
        """Show all hidden columns."""
        if not self.hidden_columns:
            QMessageBox.information(self, 'No Hidden Columns', 'No columns are currently hidden.')
            return
        
        hidden_count = len(self.hidden_columns)
        self.hidden_columns.clear()
        self._refresh_data_view()
        
        QMessageBox.information(
            self,
            'Columns Restored',
            f'Restored {hidden_count} hidden column(s).'
        )
    
    def _hide_never_map_columns(self):
        """Hide all columns that are in the never map rules."""
        current_df = self.version_manager.get_current_data()
        if current_df is None:
            return
        
        # Find never-map columns in current data
        never_map_columns = [col for col in current_df.columns if col in self.never_map_rules]
        
        if not never_map_columns:
            QMessageBox.information(
                self,
                'No Never-Map Columns',
                'No columns found that match the never-map rules.'
            )
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            'Hide Never-Map Columns',
            f'Hide {len(never_map_columns)} column(s) that will never be mapped to Pete?\n\n'
            f'Columns: {", ".join(never_map_columns[:5])}'
            f'{"..." if len(never_map_columns) > 5 else ""}',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Add to hidden columns
            for col in never_map_columns:
                self.hidden_columns.add(col)
            
            # Clear selection if any selected columns were hidden
            self.selected_columns = [col for col in self.selected_columns if col not in never_map_columns]
            
            # Refresh view
            self._refresh_data_view()
            
            QMessageBox.information(
                self,
                'Never-Map Columns Hidden',
                f'Hidden {len(never_map_columns)} never-map column(s).\n'
                'These columns won\'t clutter your data preparation view!'
            )
    
    def _hide_specific_columns(self, columns_to_hide: List[str]):
        """Hide specific columns."""
        for col in columns_to_hide:
            self.hidden_columns.add(col)
        
        # Remove hidden columns from selection
        self.selected_columns = [col for col in self.selected_columns if col not in columns_to_hide]
        
        # Refresh view
        self._refresh_data_view()
    
    def get_version_summary(self) -> Dict[str, Any]:
        """Get summary of data preparation changes."""
        history = self.version_manager.get_version_history()
        current_df = self.version_manager.get_current_data()
        
        return {
            'original_columns': len(self.original_df.columns),
            'current_columns': len(current_df.columns) if current_df is not None else 0,
            'total_versions': len(history),
            'changes_made': len(history) - 1,  # Subtract initial version
            'version_history': history,
            'hidden_columns': len(self.hidden_columns),
            'never_map_rules': len(self.never_map_rules)
        }