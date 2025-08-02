"""
Data Tools Panel

Prominent UI panel showing all data preparation tools organized by category.
Appears immediately after file upload, before Pete mapping.
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Callable
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QGroupBox, QGridLayout, QFrame, QSplitter, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal

from frontend.components.base_component import BaseComponent
from frontend.data_prep import DataPrepEditor
from frontend.dialogs.duplicate_removal_dialog import DuplicateRemovalDialog


class DataToolsPanel(BaseComponent):
    """
    Prominent data tools panel that appears immediately after upload.
    
    Organized into clear categories:
    - Column Tools: Hide, Show, Merge, Rename
    - Row Tools: Sort, Filter, Group
    - Content Tools: Clean, Transform, Validate
    """
    
    # Signal when ready to proceed to Pete mapping
    ready_for_pete_mapping = pyqtSignal(pd.DataFrame, dict)  # data + mapping_config
    
    def __init__(self, parent=None, df: Optional[pd.DataFrame] = None,
                 data_source: str = "Unknown",
                 on_back: Optional[Callable] = None,
                 on_proceed: Optional[Callable] = None):
        """
        Initialize the data tools panel.
        
        Args:
            parent: Parent widget
            df: DataFrame to work with
            data_source: Source name (e.g., "REISIFT") for mapping presets
            on_back: Back callback
            on_proceed: Proceed callback
        """
        super().__init__(parent, show_logo=True, show_navigation=True,
                         on_back=on_back, on_exit=None)
        
        if df is None:
            raise ValueError("DataFrame is required")
            
        self.original_df = df.copy()
        self.data_source = data_source
        self.on_proceed = on_proceed
        
        # Initialize the embedded data prep editor
        self.data_prep_editor = DataPrepEditor(
            parent=self,
            df=df,
            on_back=None,  # Handled by this panel
            on_proceed=self._on_data_ready
        )
        
        self._setup_ui()
        self._apply_source_presets()
    
    def _setup_ui(self):
        """Setup the tools-focused UI."""
        # Title with data source info
        title_layout = QHBoxLayout()
        
        title = QLabel(f'🛠️ Prepare {self.data_source} Data for Pete')
        title.setStyleSheet('font-size: 20px; font-weight: bold; color: #1976d2;')
        title_layout.addWidget(title)
        
        # Clear data flow indicator
        flow_label = QLabel(f'📊 FROM: {self.data_source} → TO: Pete')
        flow_label.setStyleSheet('font-size: 14px; color: #1976d2; font-weight: bold; background-color: #e3f2fd; padding: 4px 8px; border-radius: 4px;')
        title_layout.addWidget(flow_label)
        
        title_layout.addStretch()
        
        # Stats
        stats = QLabel(f'{len(self.original_df)} rows × {len(self.original_df.columns)} columns')
        stats.setStyleSheet('font-size: 12px; color: #666;')
        title_layout.addWidget(stats)
        
        self.layout.addLayout(title_layout)
        
        # Main content: Tools + Data Editor
        main_splitter = QSplitter(Qt.Vertical)
        
        # Top: Prominent Tools Panel
        tools_panel = self._create_tools_panel()
        main_splitter.addWidget(tools_panel)
        
        # Bottom: Data Editor
        main_splitter.addWidget(self.data_prep_editor)
        
        # Set sizes: 30% tools, 70% data editor
        main_splitter.setSizes([200, 600])
        
        self.layout.addWidget(main_splitter)
        
        # Bottom: Action buttons
        self._create_action_buttons()
    
    def _create_tools_panel(self) -> QFrame:
        """Create the prominent tools panel."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        
        # Column Tools
        column_tools = self._create_tool_group(
            "📋 Column Tools",
            [
                ("🔗 Merge Columns", "Combine 2+ columns into one (e.g., Notes field)", self._merge_columns),
                ("👁️‍🗨️ Hide Columns", "Hide selected columns from view", self._hide_columns),
                ("🚫 Hide Never-Map", "Auto-hide fields that won't map to Pete", self._hide_never_map),
                ("✏️ Rename Column", "Rename a column", self._rename_column),
                ("📊 Show All", "Show all hidden columns", self._show_all_columns)
            ]
        )
        layout.addWidget(column_tools)
        
        # Row Tools  
        row_tools = self._create_tool_group(
            "📏 Row Tools",
            [
                ("🔽 Sort Rows", "Sort data by column values", self._sort_rows),
                ("🔍 Filter Rows", "Filter rows by criteria", self._filter_rows),
                ("📦 Group Rows", "Group similar rows together", self._group_rows),
                ("🧹 Remove Duplicates", "Remove duplicate rows", self._remove_duplicates),
                ("📈 Sample Data", "Show sample of large datasets", self._sample_data)
            ]
        )
        layout.addWidget(row_tools)
        
        # Content Tools
        content_tools = self._create_tool_group(
            "🧽 Content Tools", 
            [
                ("🧹 Clean Data", "Remove empty values, trim spaces", self._clean_data),
                ("🔄 Transform", "Convert data types, formats", self._transform_data),
                ("✅ Validate", "Check data quality, find issues", self._validate_data),
                ("🏷️ Tag Columns", "Mark columns by type/purpose", self._tag_columns),
                ("💾 Save Preset", f"Save {self.data_source}→Pete mapping preset", self._save_preset),
                ("🚫 Strip .0", "Remove trailing .0 from numeric-like strings", self._strip_trailing_dot)
            ]
        )
        layout.addWidget(content_tools)
        
        return panel
    
    def _create_tool_group(self, title: str, tools: List[tuple]) -> QGroupBox:
        """Create a group of tools."""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #333;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        for tool_name, tooltip, callback in tools:
            btn = QPushButton(tool_name)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 12px;
                    margin: 2px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    background-color: white;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #1976d2;
                }
                QPushButton:pressed {
                    background-color: #1976d2;
                    color: white;
                }
            """)
            layout.addWidget(btn)
        
        layout.addStretch()
        return group
    
    def _create_action_buttons(self):
        """Create main action buttons."""
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_btn = QPushButton('🔄 Reset to Original')
        reset_btn.clicked.connect(self._reset_data)
        reset_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel('✏️ Preparing data...')
        self.status_label.setStyleSheet('color: #666; font-style: italic;')
        button_layout.addWidget(self.status_label)
        
        button_layout.addStretch()
        
        # Proceed button
        proceed_btn = QPushButton(f'➡️ Map {self.data_source} → Pete Headers')
        proceed_btn.clicked.connect(self._proceed_to_pete)
        proceed_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(proceed_btn)
        
        self.layout.addLayout(button_layout)
    
    def _apply_source_presets(self):
        """Apply data source specific presets (e.g., REISIFT → Pete)."""
        if self.data_source.upper() == "REISIFT":
            # Auto-apply REISIFT→Pete specific settings
            self.status_label.setText('🎯 REISIFT→Pete preset loaded - never-map fields auto-detected')
            # Auto-hide never-map fields for REISIFT
            self._hide_never_map()
        else:
            self.status_label.setText(f'📊 {self.data_source}→Pete data loaded - use tools to prepare')
    
    # Tool action methods (delegate to data prep editor)
    def _merge_columns(self):
        """Merge selected columns."""
        self.status_label.setText('🔗 Select 2+ columns in the table below, then use merge tools')
        # Focus on the data editor
        self.data_prep_editor.setFocus()
    
    def _hide_columns(self):
        """Hide selected columns."""
        self.status_label.setText('👁️‍🗨️ Select columns to hide, then use hide controls')
        self.data_prep_editor.setFocus()
    
    def _hide_never_map(self):
        """Hide never-map columns."""
        # Directly call the data editor's method
        self.data_prep_editor._hide_never_map_columns()
        self.status_label.setText('🚫 Never-map fields hidden')
    
    def _rename_column(self):
        """Rename a column."""
        self.status_label.setText('✏️ Select one column to rename')
        self.data_prep_editor.setFocus()
    
    def _show_all_columns(self):
        """Show all hidden columns."""
        self.data_prep_editor._show_hidden_columns()
        self.status_label.setText('👁️ All columns shown')
    
    def _sort_rows(self):
        """Sort rows by column."""
        self.status_label.setText('🔽 Sort feature coming soon - select columns to sort by')
    
    def _filter_rows(self):
        """Filter rows."""
        self.status_label.setText('🔍 Filter feature coming soon - define filter criteria')
    
    def _group_rows(self):
        """Group rows."""
        self.status_label.setText('📦 Group feature coming soon - select grouping columns')
    
    def _remove_duplicates(self):
        """Remove duplicate rows with dialog for parameters."""
        if not hasattr(self.data_prep_editor, 'version_manager'):
            self.status_label.setText('❌ Data preparation editor not available')
            return
        
        current_df = self.data_prep_editor.version_manager.get_current_data()
        if current_df is None:
            self.status_label.setText('❌ No data available')
            return
        
        # Show duplicate removal dialog
        dialog = DuplicateRemovalDialog(current_df.columns.tolist(), parent=self)
        if dialog.exec_() == dialog.Accepted:
            config = dialog.get_config()
            if config:
                self._apply_duplicate_removal(config)
    
    def _apply_duplicate_removal(self, config):
        """Apply duplicate removal with specified configuration."""
        current_df = self.data_prep_editor.version_manager.get_current_data()
        if current_df is None:
            return
        
        try:
            original_count = len(current_df)
            
            # Apply duplicate removal based on configuration
            if config['method'] == 'all_columns':
                # Remove duplicates based on all columns
                new_df = current_df.drop_duplicates(keep=config['keep'])
            elif config['method'] == 'selected_columns':
                # Remove duplicates based on selected columns only
                subset_columns = config['columns']
                new_df = current_df.drop_duplicates(subset=subset_columns, keep=config['keep'])
            elif config['method'] == 'ignore_case':
                # Case-insensitive duplicate removal
                if config.get('columns'):
                    # Create temporary columns with lowercase values for comparison
                    temp_df = current_df.copy()
                    for col in config['columns']:
                        if temp_df[col].dtype == 'object':  # String columns only
                            temp_df[f'{col}_lower'] = temp_df[col].astype(str).str.lower()
                    
                    # Get original columns + temp lowercase columns
                    comparison_cols = config['columns'] + [f'{col}_lower' for col in config['columns'] if temp_df[col].dtype == 'object']
                    temp_df = temp_df.drop_duplicates(subset=comparison_cols, keep=config['keep'])
                    
                    # Remove temporary columns and return
                    temp_cols_to_drop = [f'{col}_lower' for col in config['columns'] if f'{col}_lower' in temp_df.columns]
                    new_df = temp_df.drop(columns=temp_cols_to_drop)
                else:
                    new_df = current_df.drop_duplicates(keep=config['keep'])
            else:
                new_df = current_df.drop_duplicates(keep=config['keep'])
            
            removed_count = original_count - len(new_df)
            
            if removed_count == 0:
                self.status_label.setText('ℹ️ No duplicates found to remove')
                return
            
            # Save version
            if config['method'] == 'selected_columns' and config.get('columns'):
                action = f"Removed {removed_count} duplicates"
                details = f"Based on columns: {', '.join(config['columns'])} (keep={config['keep']})"
            else:
                action = f"Removed {removed_count} duplicates"
                details = f"Method: {config['method']} (keep={config['keep']})"
            
            self.data_prep_editor.version_manager.save_version(new_df, action, details)
            self.data_prep_editor._refresh_data_view()
            
            self.status_label.setText(f'✅ Removed {removed_count} duplicate rows ({len(new_df)} rows remaining)')
            
        except Exception as e:
            self.status_label.setText(f'❌ Error removing duplicates: {str(e)}')
    
    def _sample_data(self):
        """Sample large datasets."""
        self.status_label.setText('📈 Data sampling coming soon')
    
    def _clean_data(self):
        """Clean data."""
        self.status_label.setText('🧹 Data cleaning coming soon')
    
    def _transform_data(self):
        """Transform data."""
        self.status_label.setText('🔄 Data transformation coming soon')
    
    def _strip_trailing_dot(self):
        """Strip trailing .0 from numeric-like strings across the dataframe."""
        from backend.utils import trailing_dot_cleanup as tdc
        current_df = self.data_prep_editor.get_prepared_data()
        if current_df is None:
            return
        cleaned = tdc.clean_dataframe(current_df)
        # Save version & refresh view
        self.data_prep_editor.version_manager.save_version(cleaned, "Strip .0", "Removed trailing .0 from numeric-like strings")
        self.data_prep_editor._refresh_data_view()

        QMessageBox.information(self, "Trailing .0 Removed", "All numeric-like strings with trailing .0 have been cleaned.")

    def _validate_data(self):
        """Validate data."""
        self.status_label.setText('✅ Data validation coming soon')
    
    def _tag_columns(self):
        """Tag columns."""
        self.status_label.setText('🏷️ Column tagging coming soon')
    
    def _save_preset(self):
        """Save current configuration as preset."""
        self.status_label.setText(f'💾 Save {self.data_source}→Pete mapping preset coming soon')
    
    def _reset_data(self):
        """Reset to original data."""
        self.data_prep_editor._reset_to_original()
        self.status_label.setText('🔄 Data reset to original')
    
    def _proceed_to_pete(self):
        """Proceed to map REISIFT data to Pete headers."""
        prepared_data = self.data_prep_editor.get_prepared_data()
        if prepared_data is None:
            return
            
        # Create mapping configuration with clear FROM→TO
        mapping_config = {
            'from_source': self.data_source,  # e.g., "REISIFT"
            'to_target': 'Pete',  # Always Pete
            'mapping_name': f'{self.data_source}→Pete',
            'original_columns': len(self.original_df.columns),
            'prepared_columns': len(prepared_data.columns),
            'preparation_summary': self.data_prep_editor.get_version_summary(),
            'preset_applied': self.data_source.upper() if self.data_source != "Unknown" else None
        }
        
        # Emit signal
        self.ready_for_pete_mapping.emit(prepared_data, mapping_config)
        
        # Call callback
        if self.on_proceed:
            self.on_proceed(prepared_data, mapping_config)
    
    def _on_data_ready(self, prepared_df: pd.DataFrame):
        """Handle when data prep editor signals data is ready."""
        self.status_label.setText('✅ Data preparation complete - ready for Pete mapping')
    
    def get_prepared_data(self) -> pd.DataFrame:
        """Get the prepared data."""
        return self.data_prep_editor.get_prepared_data()
    
    def get_preparation_summary(self) -> Dict[str, Any]:
        """Get summary of all preparation work done."""
        return {
            'data_source': self.data_source,
            'original_shape': self.original_df.shape,
            'prepared_shape': self.get_prepared_data().shape,
            'tools_used': [],  # TODO: Track which tools were used
            'version_summary': self.data_prep_editor.get_version_summary()
        }