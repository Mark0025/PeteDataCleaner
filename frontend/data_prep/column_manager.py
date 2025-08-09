"""
Column Hiding Manager

Manages column visibility and never-map rules for data preparation.
"""

import json
import os
import pandas as pd
from typing import Set, List, Dict, Any, Optional
from PyQt5.QtWidgets import QMessageBox


class ColumnHidingManager:
    """Manages column hiding and visibility rules."""
    
    def __init__(self, parent_widget=None):
        self.hidden_columns: Set[str] = set()
        self.never_map_rules: List[str] = []
        self.parent_widget = parent_widget
        self._load_never_map_rules()
    
    def _load_never_map_rules(self) -> None:
        """Load never map rules from mapping_rules.json"""
        try:
            rules_path = os.path.join("data", "mappings", "mapping_rules.json")
            if os.path.exists(rules_path):
                with open(rules_path, 'r') as f:
                    rules = json.load(f)
                    self.never_map_rules = rules.get('never_map', [])
        except Exception as e:
            print(f"Warning: Could not load never map rules: {e}")
    
    def is_hidden(self, column: str) -> bool:
        """Check if a column is hidden."""
        return column in self.hidden_columns
    
    def is_never_map(self, column: str) -> bool:
        """Check if a column is in never map rules."""
        return column in self.never_map_rules
    
    def hide_columns(self, columns: List[str]) -> int:
        """Hide specified columns. Returns number of columns hidden."""
        hidden_count = 0
        for col in columns:
            if col not in self.hidden_columns:
                self.hidden_columns.add(col)
                hidden_count += 1
        return hidden_count
    
    def show_all_columns(self) -> int:
        """Show all hidden columns. Returns number of columns restored."""
        hidden_count = len(self.hidden_columns)
        self.hidden_columns.clear()
        return hidden_count
    
    def get_visible_columns(self, all_columns: List[str]) -> List[str]:
        """Get list of visible columns from all columns."""
        return [col for col in all_columns if col not in self.hidden_columns]
    
    def get_never_map_columns(self, all_columns: List[str]) -> List[str]:
        """Get list of never-map columns that exist in the data."""
        return [col for col in all_columns if col in self.never_map_rules]
    
    def hide_never_map_columns(self, all_columns: List[str]) -> bool:
        """Hide all never-map columns. Returns True if any were hidden."""
        never_map_columns = self.get_never_map_columns(all_columns)
        
        if not never_map_columns:
            if self.parent_widget:
                QMessageBox.information(
                    self.parent_widget,
                    'No Never-Map Columns',
                    'No columns found that match the never-map rules.'
                )
            return False
        
        # Confirm with user
        if self.parent_widget:
            reply = QMessageBox.question(
                self.parent_widget,
                'Hide Never-Map Columns',
                f'Hide {len(never_map_columns)} column(s) that will never be mapped to Pete?\n\n'
                f'Columns: {", ".join(never_map_columns[:5])}'
                f'{"..." if len(never_map_columns) > 5 else ""}',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return False
        
        # Hide the columns
        hidden_count = self.hide_columns(never_map_columns)
        
        if self.parent_widget and hidden_count > 0:
            QMessageBox.information(
                self.parent_widget,
                'Never-Map Columns Hidden',
                f'Hidden {hidden_count} never-map column(s).\n'
                'These columns won\'t clutter your data preparation view!'
            )
        
        return hidden_count > 0
    
    def get_header_display_name(self, column: str) -> str:
        """Get display name for column header with never-map indicator."""
        # Truncate long column names for display
        display_name = column if len(column) <= 20 else column[:17] + "..."
        
        # Mark never-map columns
        if self.is_never_map(column):
            display_name = f"🚫 {display_name}"
            
        return display_name
    
    def get_column_tooltip(self, column: str, row: int, value: str) -> str:
        """Get enhanced tooltip for column with never-map indication."""
        tooltip = f"Column: {column}\nRow: {row+1}\nValue: {value}"
        if self.is_never_map(column):
            tooltip += "\n🚫 This column will never be mapped to Pete"
        return tooltip
    
    def get_stats_text(self, total_rows: int, total_columns: int) -> str:
        """Get stats text with hidden column information."""
        visible_columns = total_columns - len(self.hidden_columns)
        hidden_count = len(self.hidden_columns)
        
        stats = f"📊 {total_rows} rows × {visible_columns}/{total_columns} columns"
        if hidden_count > 0:
            stats += f" ({hidden_count} hidden)"
        
        return stats
    
    def get_hidden_indicator_text(self) -> str:
        """Get text for hidden columns indicator."""
        hidden_count = len(self.hidden_columns)
        if hidden_count == 0:
            return ""
        
        never_map_hidden = sum(1 for col in self.hidden_columns if col in self.never_map_rules)
        text = f"Hidden: {hidden_count} columns"
        if never_map_hidden > 0:
            text += f" ({never_map_hidden} never-map)"
        
        return text
    
    def filter_selected_columns(self, selected_columns: List[str]) -> List[str]:
        """Remove hidden columns from selected columns list."""
        return [col for col in selected_columns if col not in self.hidden_columns]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of column hiding state."""
        return {
            'hidden_columns': len(self.hidden_columns),
            'never_map_rules': len(self.never_map_rules),
            'hidden_column_list': list(self.hidden_columns),
            'never_map_rule_list': self.never_map_rules
        }