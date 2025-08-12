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
from frontend.utils.resizable_widget import create_tools_panel


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
        
        # Main content: Tools + Data Editor using resizable widget
        tools_panel = self._create_tools_panel()
        
        # Create resizable panel with tools on left, data editor on right
        self.resizable_panel = create_tools_panel(
            tools_widget=tools_panel,
            content_widget=self.data_prep_editor,
            tools_title="🛠️ Data Tools",
            content_title="📊 Data Editor"
        )
        
        self.layout.addWidget(self.resizable_panel)
        
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
                ("📞 Prioritize Phones", "Select best 5 phones for Pete", self._prioritize_phones),
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
                ("📞 Prioritize Phones", "Prioritize phone numbers", self._prioritize_phones),
                ("🏠 Owner Analysis", "Analyze property ownership patterns", self._analyze_owners),
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
            elif config['method'] == 'address_based_grouping':
                # Address-based grouping (basic version)
                new_df = current_df.drop_duplicates(subset=['Property address'], keep=config['keep'])
            elif config['method'] == 'smart_seller_creation':
                # Smart seller creation with phone prioritization
                from backend.utils.ownership_analysis import deduplicate_by_mailing_address
                new_df = deduplicate_by_mailing_address(current_df)
            else:
                new_df = current_df.drop_duplicates(keep=config['keep'])
            
            removed_count = original_count - len(new_df)
            
            if removed_count == 0:
                self.status_label.setText('ℹ️ No duplicates found to remove')
                return
            
            # Save version
            if config['method'] == 'smart_seller_creation':
                action = f"Smart Seller Creation"
                details = f"Created Seller 1-5 structure with phone prioritization ({len(new_df)} records)"
                self.status_label.setText(f'✅ Smart Seller Creation complete ({len(new_df)} Pete-ready records)')
            elif config['method'] == 'address_based_grouping':
                action = f"Address-based grouping"
                details = f"Grouped by Property Address, removed {removed_count} duplicates"
                self.status_label.setText(f'✅ Address-based grouping complete ({len(new_df)} records)')
            elif config['method'] == 'selected_columns' and config.get('columns'):
                action = f"Removed {removed_count} duplicates"
                details = f"Based on columns: {', '.join(config['columns'])} (keep={config['keep']})"
                self.status_label.setText(f'✅ Removed {removed_count} duplicate rows ({len(new_df)} rows remaining)')
            else:
                action = f"Removed {removed_count} duplicates"
                details = f"Method: {config['method']} (keep={config['keep']})"
                self.status_label.setText(f'✅ Removed {removed_count} duplicate rows ({len(new_df)} rows remaining)')
            
            self.data_prep_editor.version_manager.save_version(new_df, action, details)
            self.data_prep_editor._refresh_data_view()
            
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
        from backend.utils.high_performance_processor import clean_dataframe_fast
        current_df = self.data_prep_editor.get_prepared_data()
        if current_df is None:
            return
        cleaned = clean_dataframe_fast(current_df)
        # Save version & refresh view
        self.data_prep_editor.version_manager.save_version(cleaned, "Strip .0", "Removed trailing .0 from numeric-like strings")
        self.data_prep_editor._refresh_data_view()

        QMessageBox.information(self, "Trailing .0 Removed", "All numeric-like strings with trailing .0 have been cleaned.")

    def _prioritize_phones(self):
        """Open dialog to prioritize phones and apply selection."""
        from backend.utils.high_performance_processor import prioritize_phones_fast  # Use fast processor
        from frontend.dialogs.phone_prioritization_dialog import PhonePrioritizationDialog

        current_df = self.data_prep_editor.get_prepared_data()
        if current_df is None:
            return
            
        # Count original phone columns
        original_phone_cols = [col for col in current_df.columns if col.startswith('Phone ') and not any(suffix in col for suffix in [' Status', ' Type', ' Tag'])]
        
        # Get initial prioritization for preview
        initial_df, meta = prioritize_phones_fast(current_df)
        dlg = PhonePrioritizationDialog(meta, current_df, self)
        
        if dlg.exec_():
            # Get the custom prioritization rules from dialog
            prioritization_rules = dlg.get_prioritization_rules()
            
            # Apply prioritization with custom rules
            cleaned_df, meta = prioritize_phones_fast(current_df, prioritization_rules=prioritization_rules)
            
            # Count remaining phone columns
            remaining_phone_cols = [col for col in cleaned_df.columns if col.startswith('Phone ') and not any(suffix in col for suffix in [' Status', ' Type', ' Tag'])]
            
            # Save version with custom rules info
            rules_summary = f"Custom rules: Status={prioritization_rules['status_weights']['CORRECT']}, Type={prioritization_rules['type_weights']['MOBILE']}, Tags={prioritization_rules['tag_weights']['call_a01']}"
            self.data_prep_editor.version_manager.save_version(
                cleaned_df, "Prioritize Phones (Custom Rules)", f"Applied custom prioritization rules: {rules_summary}"
            )
            self.data_prep_editor._refresh_data_view()
            
            # Update status with clear feedback
            reduced_count = len(original_phone_cols) - len(remaining_phone_cols)
            self.status_label.setText(f'📞 Phone prioritization applied with custom rules: {len(original_phone_cols)} → {len(remaining_phone_cols)} columns ({reduced_count} removed)')

    def _analyze_owners(self):
        """Analyze property ownership patterns and business entities."""
        from backend.utils.owner_analyzer import OwnerAnalyzer
        from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
        from PyQt5.QtCore import Qt

        current_df = self.data_prep_editor.get_prepared_data()
        if current_df is None:
            return
        
        try:
            # Perform ownership analysis
            analyzer = OwnerAnalyzer()
            results = analyzer.analyze_ownership(current_df)
            
            # Store results for preset saving
            self.last_owner_analysis_results = results
            
            # Create analysis dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("🏠 Property Ownership Analysis")
            dialog.resize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # Title
            title = QLabel("Property Ownership Analysis Results")
            title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
            layout.addWidget(title)
            
            # Analysis text
            analysis_text = QTextEdit()
            analysis_text.setReadOnly(True)
            
            # Generate detailed report
            report = analyzer.generate_report(results)
            
            # Add key insights
            insights = f"""
{report}

🎯 KEY INSIGHTS:
• {results['total_owners']:,} unique owners identified
• {results['business_entities']['business_count']:,} business entities detected
• {results['ownership_patterns']['owners_with_multiple_properties']:,} owners with multiple properties
• {results['ownership_patterns']['max_properties_per_owner']} max properties per owner

🏢 BUSINESS ENTITIES:
{chr(10).join(f"• {entity}" for entity in results['business_entities']['sample_businesses'][:5])}

👤 TOP PROPERTY OWNERS:
{chr(10).join(f"• {owner}: {count} properties" for owner, count in list(results['ownership_patterns']['top_owners'].items())[:5])}

📊 MARKETING OPPORTUNITIES:
• High-value targets: {len(results['marketing_insights']['high_value_targets'])}
• Multi-property opportunities: {len(results['marketing_insights']['multi_property_opportunities'])}
• Business entity opportunities: {len(results['marketing_insights']['business_entity_opportunities'])}
"""
            
            analysis_text.setPlainText(insights)
            layout.addWidget(analysis_text)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            export_btn = QPushButton("📁 Export Analysis")
            export_btn.clicked.connect(lambda: self._export_owner_analysis(results))
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            
            button_layout.addWidget(export_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            # Show dialog
            dialog.exec_()
            
            self.status_label.setText(f'🏠 Ownership analysis complete: {results["total_owners"]:,} owners analyzed')
            
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Error during ownership analysis: {str(e)}")
            self.status_label.setText('❌ Ownership analysis failed')

    def _export_owner_analysis(self, results):
        """Export owner analysis results."""
        from backend.utils.owner_analyzer import OwnerAnalyzer
        import os
        
        try:
            # Create export directory if it doesn't exist
            export_dir = "data/exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Export analysis
            analyzer = OwnerAnalyzer()
            export_file = os.path.join(export_dir, "owner_analysis_export.json")
            analyzer.export_owner_data(results, export_file)
            
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Export Complete", f"Owner analysis exported to:\n{export_file}")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Error", f"Error exporting analysis: {str(e)}")

    def _validate_data(self):
        """Validate data."""
        self.status_label.setText('✅ Data validation coming soon')
    
    def _tag_columns(self):
        """Tag columns."""
        self.status_label.setText('🏷️ Column tagging coming soon')
    
    def _save_preset(self):
        """Save comprehensive preset with all analysis data and configurations."""
        from backend.utils.preset_manager import PresetManager
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        try:
            # Get preset name from user
            preset_name, ok = QInputDialog.getText(
                self, 
                "Save Preset", 
                f"Enter name for {self.data_source}→Pete preset:",
                text=f"{self.data_source}_preset"
            )
            
            if not ok or not preset_name.strip():
                return
            
            # Get current data
            prepared_data = self.data_prep_editor.get_prepared_data()
            if prepared_data is None:
                QMessageBox.warning(self, "No Data", "No prepared data to save.")
                return
            
            # Get phone prioritization rules if any were applied
            phone_rules = None
            version_summary = self.data_prep_editor.get_version_summary()
            for version in version_summary:
                if "phone prioritization" in version.get('action', '').lower():
                    # Try to extract rules from version details
                    phone_rules = self._extract_phone_rules_from_version(version)
                    break
            
            # Get owner analysis results if available
            owner_analysis = getattr(self, 'last_owner_analysis_results', None)
            
            # Get data preparation summary
            data_prep_summary = {
                'version_summary': version_summary,
                'tools_used': self._get_used_tools(),
                'data_source': self.data_source,
                'original_shape': self.original_df.shape,
                'prepared_shape': prepared_data.shape
            }
            
            # Save comprehensive preset using user system
            from backend.utils.user_manager import user_manager
            
            if user_manager.current_user:
                preset_path = user_manager.save_user_preset(
                    preset_name=preset_name,
                    original_df=self.original_df,
                    prepared_df=prepared_data,
                    phone_prioritization_rules=phone_rules,
                    owner_analysis_results=owner_analysis,
                    data_prep_summary=data_prep_summary
                )
            else:
                # Fallback to direct preset manager
                manager = PresetManager()
                preset_path = manager.save_comprehensive_preset(
                    preset_name=preset_name,
                    data_source=self.data_source,
                    original_df=self.original_df,
                    prepared_df=prepared_data,
                    phone_prioritization_rules=phone_rules,
                    owner_analysis_results=owner_analysis,
                    data_prep_summary=data_prep_summary
                )
            
            QMessageBox.information(
                self, 
                "Preset Saved", 
                f"Comprehensive preset saved successfully!\n\n"
                f"Location: {preset_path}\n\n"
                f"Includes:\n"
                f"• Phone prioritization rules\n"
                f"• Data preparation steps\n"
                f"• Data samples and quality metrics\n"
                f"• Reference views and reports"
            )
            
            self.status_label.setText(f'💾 Comprehensive preset saved: {preset_name}')
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Error saving preset: {str(e)}")
            self.status_label.setText('❌ Preset save failed')
    
    def _extract_phone_rules_from_version(self, version: Dict) -> Optional[Dict]:
        """Extract phone prioritization rules from version details."""
        # Default rules - in a real implementation, you'd store these when applied
        return {
            'status_weights': {
                'CORRECT': 100, 'UNKNOWN': 80, 'NO_ANSWER': 60, 
                'WRONG': 40, 'DEAD': 20, 'DNC': 10
            },
            'type_weights': {
                'MOBILE': 100, 'LANDLINE': 80, 'UNKNOWN': 60
            },
            'tag_weights': {
                'call_a01': 100, 'call_a02': 90, 'call_a03': 80,
                'call_a04': 70, 'call_a05': 60, 'no_tag': 50
            },
            'call_count_multiplier': 1.0
        }
    
    def _get_used_tools(self) -> List[str]:
        """Get list of tools that were used during data preparation."""
        tools_used = []
        version_summary = self.data_prep_editor.get_version_summary()
        
        for version in version_summary:
            action = version.get('action', '').lower()
            if 'strip' in action and '.0' in action:
                tools_used.append('strip_trailing_dot')
            elif 'prioritize' in action and 'phone' in action:
                tools_used.append('phone_prioritization')
            elif 'duplicate' in action:
                tools_used.append('duplicate_removal')
            elif 'clean' in action:
                tools_used.append('data_cleaning')
        
        return tools_used
    
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