"""
Data Preparation Editor

Streamlined main component that orchestrates data preparation workflow.
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Callable
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu, QAction,
    QMessageBox, QInputDialog, QGroupBox, QSplitter, QTextEdit,
    QScrollArea, QFrame, QListWidget
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from frontend.components.base_component import BaseComponent
from .version_manager import DataVersionManager
from .concatenation_dialog import SmartConcatenationDialog
from .column_manager import ColumnHidingManager


class DataPrepEditor(BaseComponent):
    """
    Streamlined data preparation editor component.
    
    Features:
    - Interactive column editing
    - Smart concatenation with multiple delimiters
    - Version history with undo/redo
    - Column hiding and never-map integration
    - Clean data preview
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
        
        # Initialize managers
        self.version_manager = DataVersionManager()
        self.version_manager.save_version(df, "Initial Upload", "Original data loaded")
        
        self.column_manager = ColumnHidingManager(parent_widget=self)
        
        # UI state
        self.selected_columns = []
        
        self._setup_ui()
        self._refresh_data_view()
    
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
        
        # Left panel - Data table and controls
        left_panel = self._create_data_panel()
        
        # Right panel - Version history and info
        right_panel = self._create_info_panel()
        
        # Set panel sizes
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 300])  # 800px for table, 300px for sidebar
        
        self.layout.addWidget(splitter)
    
    def _create_data_panel(self) -> QFrame:
        """Create the main data editing panel."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Data manipulation controls
        layout.addLayout(self._create_data_controls())
        
        # Column visibility controls
        layout.addLayout(self._create_visibility_controls())
        
        # Data table
        self.data_table = self._create_data_table()
        layout.addWidget(self.data_table)
        
        # Action buttons
        layout.addLayout(self._create_action_buttons())
        
        return panel
    
    def _create_data_controls(self) -> QHBoxLayout:
        """Create data manipulation controls."""
        controls = QHBoxLayout()
        
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
        controls.addWidget(self.merge_btn)
        
        self.rename_btn = QPushButton('✏️ Rename Column')
        self.rename_btn.setEnabled(False)
        self.rename_btn.clicked.connect(self._rename_column)
        controls.addWidget(self.rename_btn)
        
        controls.addStretch()
        
        # Version controls
        self.undo_btn = QPushButton('↶ Undo')
        self.undo_btn.setEnabled(False)
        self.undo_btn.clicked.connect(self._undo)
        controls.addWidget(self.undo_btn)
        
        self.redo_btn = QPushButton('↷ Redo')
        self.redo_btn.setEnabled(False)
        self.redo_btn.clicked.connect(self._redo)
        controls.addWidget(self.redo_btn)
        
        return controls
    
    def _create_visibility_controls(self) -> QHBoxLayout:
        """Create column visibility controls."""
        controls = QHBoxLayout()
        
        self.hide_btn = QPushButton('👁️‍🗨️ Hide Selected')
        self.hide_btn.setEnabled(False)
        self.hide_btn.clicked.connect(self._hide_selected_columns)
        self.hide_btn.setToolTip('Hide selected columns from view')
        controls.addWidget(self.hide_btn)
        
        self.show_hidden_btn = QPushButton('👁️ Show Hidden')
        self.show_hidden_btn.clicked.connect(self._show_hidden_columns)
        self.show_hidden_btn.setToolTip('Show all hidden columns')
        controls.addWidget(self.show_hidden_btn)
        
        self.hide_never_map_btn = QPushButton('🚫 Hide Never-Map Fields')
        self.hide_never_map_btn.clicked.connect(self._hide_never_map_columns)
        self.hide_never_map_btn.setToolTip('Hide columns that will never be mapped to Pete')
        controls.addWidget(self.hide_never_map_btn)
        
        controls.addStretch()
        
        # Hidden columns indicator
        self.hidden_indicator = QLabel()
        self.hidden_indicator.setStyleSheet('color: #666; font-style: italic;')
        controls.addWidget(self.hidden_indicator)
        
        return controls
    
    def _create_data_table(self) -> QTableWidget:
        """Create the data table widget with drag-and-drop support."""
        table = QTableWidget()
        table.setSelectionBehavior(QAbstractItemView.SelectColumns)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._show_context_menu)
        table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Enable drag-and-drop for column reordering
        table.setDragDropMode(QAbstractItemView.InternalMove)
        table.setDragDropOverwriteMode(False)
        table.setDefaultDropAction(Qt.MoveAction)
        
        # Allow moving columns by dragging headers
        header = table.horizontalHeader()
        header.setSectionsMovable(True)
        header.setDragDropMode(QAbstractItemView.InternalMove)
        header.sectionMoved.connect(self._on_column_moved)
        
        # Style the table for better readability
        table.setStyleSheet("""
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
                background-color: #1976d2;
                color: white;
                padding: 10px;
                border: 1px solid #1565c0;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:hover {
                background-color: #1565c0;
                cursor: move;
            }
        """)
        
        return table
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Create action buttons."""
        layout = QHBoxLayout()
        layout.addStretch()
        
        self.reset_btn = QPushButton('🔄 Reset to Original')
        self.reset_btn.clicked.connect(self._reset_to_original)
        layout.addWidget(self.reset_btn)
        
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
        layout.addWidget(self.proceed_btn)
        
        return layout
    
    def _create_info_panel(self) -> QFrame:
        """Create the information panel."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        # Version history
        history_label = QLabel('📚 Version History')
        history_label.setStyleSheet('font-weight: bold; font-size: 14px; margin-bottom: 5px;')
        layout.addWidget(history_label)
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(200)
        layout.addWidget(self.history_list)
        
        # Column info
        info_label = QLabel('ℹ️ Column Information')
        info_label.setStyleSheet('font-weight: bold; font-size: 14px; margin: 10px 0 5px 0;')
        layout.addWidget(info_label)
        
        self.column_info = QTextEdit()
        self.column_info.setMaximumHeight(150)
        self.column_info.setReadOnly(True)
        layout.addWidget(self.column_info)
        
        layout.addStretch()
        
        return panel
    
    def _refresh_data_view(self):
        """Refresh the data table view with current data."""
        current_df = self.version_manager.get_current_data()
        if current_df is None:
            return
        
        # Get visible columns and create display DataFrame
        visible_columns = self.column_manager.get_visible_columns(list(current_df.columns))
        display_df = current_df[visible_columns] if visible_columns else current_df
        
        # Update stats
        self.stats_label.setText(
            self.column_manager.get_stats_text(len(current_df), len(current_df.columns))
        )
        
        # Update hidden columns indicator
        self.hidden_indicator.setText(self.column_manager.get_hidden_indicator_text())
        
        # Update table
        self._populate_table(display_df, visible_columns)
        
        # Update controls
        self._update_controls()
        self._update_version_history()
    
    def _populate_table(self, display_df: pd.DataFrame, visible_columns: List[str]):
        """Populate the data table."""
        self.data_table.clear()
        self.data_table.setRowCount(min(20, len(display_df)))
        self.data_table.setColumnCount(len(visible_columns))
        
        # Set headers with never-map indicators
        headers = [self.column_manager.get_header_display_name(col) for col in visible_columns]
        self.data_table.setHorizontalHeaderLabels(headers)
        
        # Populate data
        for i in range(min(20, len(display_df))):
            for j, col in enumerate(visible_columns):
                value = str(display_df.iloc[i, j]) if pd.notna(display_df.iloc[i, j]) else ""
                item = QTableWidgetItem(value)
                
                # Enhanced tooltip with never-map indication
                tooltip = self.column_manager.get_column_tooltip(col, i, value)
                item.setToolTip(tooltip)
                
                self.data_table.setItem(i, j, item)
        
        # Auto-resize columns for better visibility
        self.data_table.resizeColumnsToContents()
        self.data_table.horizontalHeader().setStretchLastSection(True)
        
        # Set minimum column widths for readability
        for i in range(self.data_table.columnCount()):
            current_width = self.data_table.columnWidth(i)
            min_width = 150
            if current_width < min_width:
                self.data_table.setColumnWidth(i, min_width)
    
    def _update_controls(self):
        """Update control button states."""
        self.undo_btn.setEnabled(self.version_manager.can_undo())
        self.redo_btn.setEnabled(self.version_manager.can_redo())
        
        self.merge_btn.setEnabled(len(self.selected_columns) >= 2)
        self.rename_btn.setEnabled(len(self.selected_columns) == 1)
        self.hide_btn.setEnabled(len(self.selected_columns) > 0)
    
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
            visible_columns = self.column_manager.get_visible_columns(list(current_df.columns))
            
            for range_item in selected_ranges:
                for col_idx in range(range_item.leftColumn(), range_item.rightColumn() + 1):
                    if col_idx < len(visible_columns):
                        col_name = visible_columns[col_idx]
                        if col_name not in self.selected_columns:
                            self.selected_columns.append(col_name)
        
        # Update controls and info
        self._update_controls()
        self._update_column_info()
    
    def _on_column_moved(self, logical_index: int, old_visual_index: int, new_visual_index: int):
        """Handle column reordering via drag-and-drop."""
        current_df = self.version_manager.get_current_data()
        if current_df is None:
            return
        
        try:
            # Get column order based on visible columns
            visible_columns = self.column_manager.get_visible_columns(list(current_df.columns))
            
            # Create new column order
            new_order = visible_columns.copy()
            if 0 <= old_visual_index < len(new_order) and 0 <= new_visual_index < len(new_order):
                # Move the column in the list
                moved_column = new_order.pop(old_visual_index)
                new_order.insert(new_visual_index, moved_column)
                
                # Reorder the DataFrame to match new column order
                # Keep hidden columns in their original positions
                all_columns = list(current_df.columns)
                hidden_columns = [col for col in all_columns if col not in visible_columns]
                
                # Create final column order: visible columns in new order + hidden columns at end
                final_order = new_order + hidden_columns
                
                # Reorder DataFrame
                new_df = current_df[final_order].copy()
                
                # Save version
                moved_col_name = moved_column
                action = f"Moved column '{moved_col_name}'"
                details = f"Position: {old_visual_index + 1} → {new_visual_index + 1}"
                self.version_manager.save_version(new_df, action, details)
                
                # Refresh view
                self._refresh_data_view()
                
        except Exception as e:
            QMessageBox.warning(
                self,
                'Column Move Error',
                f'Failed to move column: {str(e)}'
            )
    
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
            never_map_selected = [col for col in self.selected_columns if self.column_manager.is_never_map(col)]
            if never_map_selected:
                never_map_action = QAction(f'🚫 Hide {len(never_map_selected)} Never-Map Column(s)', self)
                never_map_action.triggered.connect(lambda: self._hide_specific_columns(never_map_selected))
                menu.addAction(never_map_action)
        
        if menu.actions():
            menu.exec_(self.data_table.mapToGlobal(pos))
    
    # Data manipulation methods
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
        
        if dialog.exec_() == dialog.Accepted:
            result = dialog.get_result()
            if result:
                self._apply_merge(result)
    
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
            include_headers = merge_config.get('include_headers', False)
            
            # Perform concatenation with optional headers
            if include_headers:
                # Include column headers in the output
                if handle_empty:
                    merged_data = new_df[columns_to_merge].apply(
                        lambda row: delimiter.join(
                            f"{col}: {val}" for col, val in zip(columns_to_merge, row)
                            if pd.notna(val) and str(val).strip()
                        ),
                        axis=1
                    )
                else:
                    merged_data = new_df[columns_to_merge].apply(
                        lambda row: delimiter.join(
                            f"{col}: {val if pd.notna(val) else ''}" for col, val in zip(columns_to_merge, row)
                        ),
                        axis=1
                    )
            else:
                # Original logic without headers
                if handle_empty:
                    merged_data = new_df[columns_to_merge].apply(
                        lambda row: delimiter.join(str(val) for val in row if pd.notna(val) and str(val).strip()),
                        axis=1
                    )
                else:
                    merged_data = new_df[columns_to_merge].apply(
                        lambda row: delimiter.join(str(val) if pd.notna(val) else "" for val in row),
                        axis=1
                    )
            
            # Remove original columns if requested
            if not keep_original:
                new_df = new_df.drop(columns=columns_to_merge)
                # Remove hidden columns that were dropped
                for col in columns_to_merge:
                    self.column_manager.hidden_columns.discard(col)
            
            # Insert merged column at the leftmost position (index 0)
            new_df.insert(0, new_column_name, merged_data)
            
            # Save version
            action = f"Merged {len(columns_to_merge)} columns"
            details = f"{' + '.join(columns_to_merge)} → {new_column_name}"
            self.version_manager.save_version(new_df, action, details)
            
            # Refresh view
            self._refresh_data_view()
            
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
                    
                    # Update hidden columns tracking
                    if current_col in self.column_manager.hidden_columns:
                        self.column_manager.hidden_columns.remove(current_col)
                        self.column_manager.hidden_columns.add(new_name)
                    
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
    
    # Version control methods
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
            self.column_manager.show_all_columns()  # Show all columns on reset
            self._refresh_data_view()
    
    # Column hiding methods
    def _hide_selected_columns(self):
        """Hide the selected columns."""
        if not self.selected_columns:
            return
        
        hidden_count = self.column_manager.hide_columns(self.selected_columns)
        self.selected_columns = []
        self._refresh_data_view()
        
        QMessageBox.information(
            self,
            'Columns Hidden',
            f'Hidden {hidden_count} column(s). Use "Show Hidden" to restore them.'
        )
    
    def _show_hidden_columns(self):
        """Show all hidden columns."""
        hidden_count = self.column_manager.show_all_columns()
        if hidden_count > 0:
            self._refresh_data_view()
            QMessageBox.information(
                self,
                'Columns Restored',
                f'Restored {hidden_count} hidden column(s).'
            )
        else:
            QMessageBox.information(self, 'No Hidden Columns', 'No columns are currently hidden.')
    
    def _hide_never_map_columns(self):
        """Hide all columns that are in the never map rules."""
        current_df = self.version_manager.get_current_data()
        if current_df is None:
            return
        
        success = self.column_manager.hide_never_map_columns(list(current_df.columns))
        if success:
            # Remove hidden columns from selection
            self.selected_columns = self.column_manager.filter_selected_columns(self.selected_columns)
            self._refresh_data_view()
    
    def _hide_specific_columns(self, columns_to_hide: List[str]):
        """Hide specific columns."""
        self.column_manager.hide_columns(columns_to_hide)
        self.selected_columns = self.column_manager.filter_selected_columns(self.selected_columns)
        self._refresh_data_view()
    
    # Navigation methods
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
    
    # Public interface methods
    def get_prepared_data(self) -> pd.DataFrame:
        """Get the current prepared data."""
        return self.version_manager.get_current_data()
    
    def get_version_summary(self) -> Dict[str, Any]:
        """Get summary of data preparation changes."""
        version_summary = self.version_manager.get_summary()
        column_summary = self.column_manager.get_summary()
        
        current_df = self.version_manager.get_current_data()
        
        return {
            'original_columns': len(self.original_df.columns),
            'current_columns': len(current_df.columns) if current_df is not None else 0,
            **version_summary,
            **column_summary
        }