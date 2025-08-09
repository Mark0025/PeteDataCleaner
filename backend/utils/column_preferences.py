#!/usr/bin/env python3
"""
Column Preferences Manager

Manages persistent column hiding preferences and automatically applies them
to new data uploads.
"""

import json
import os
from typing import List, Set, Dict, Any
from pathlib import Path
from loguru import logger
import pandas as pd


class ColumnPreferences:
    """
    Manages column hiding preferences and automatically applies them.
    
    Features:
    - Persistent storage of hidden columns
    - Auto-hide columns based on data patterns
    - Per-file and global preferences
    - Automatic application on data load
    """
    
    def __init__(self, base_dir: str = "data/users/preferences"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.preferences_file = self.base_dir / "column_preferences.json"
        self.hidden_columns_file = self.base_dir / "hidden_columns.json"
        
        # Load existing preferences
        self.preferences = self._load_preferences()
        self.hidden_columns = self._load_hidden_columns()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load column preferences from file."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load preferences: {e}")
        
        return {
            'auto_hide_empty_threshold': 0.9,
            'auto_hide_patterns': [
                '^Unnamed:',
                '^Column',
                '^col_',
                '^temp_',
                '^_',
                '^id$',
                '^index$'
            ],
            'always_show_columns': [
                'First Name', 'Last Name', 'Property address', 'Property city',
                'Property state', 'Property zip', 'Phone', 'Email', 'Estimated value'
            ],
            'file_specific_preferences': {}
        }
    
    def _load_hidden_columns(self) -> Dict[str, List[str]]:
        """Load hidden columns from file."""
        if self.hidden_columns_file.exists():
            try:
                with open(self.hidden_columns_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load hidden columns: {e}")
        
        return {
            'global_hidden': [],
            'file_specific': {}
        }
    
    def _save_preferences(self):
        """Save preferences to file."""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
    
    def _save_hidden_columns(self):
        """Save hidden columns to file."""
        try:
            with open(self.hidden_columns_file, 'w') as f:
                json.dump(self.hidden_columns, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save hidden columns: {e}")
    
    def add_hidden_columns(self, columns: List[str], file_name: str = None):
        """
        Add columns to hidden list.
        
        Args:
            columns: List of column names to hide
            file_name: Optional file name for file-specific hiding
        """
        if file_name:
            if file_name not in self.hidden_columns['file_specific']:
                self.hidden_columns['file_specific'][file_name] = []
            self.hidden_columns['file_specific'][file_name].extend(columns)
            # Remove duplicates
            self.hidden_columns['file_specific'][file_name] = list(set(
                self.hidden_columns['file_specific'][file_name]
            ))
        else:
            self.hidden_columns['global_hidden'].extend(columns)
            # Remove duplicates
            self.hidden_columns['global_hidden'] = list(set(
                self.hidden_columns['global_hidden']
            ))
        
        self._save_hidden_columns()
        logger.info(f"Added {len(columns)} columns to hidden list")
    
    def get_hidden_columns(self, file_name: str = None) -> List[str]:
        """
        Get list of hidden columns.
        
        Args:
            file_name: Optional file name for file-specific columns
            
        Returns:
            List of hidden column names
        """
        hidden = self.hidden_columns['global_hidden'].copy()
        
        if file_name and file_name in self.hidden_columns['file_specific']:
            hidden.extend(self.hidden_columns['file_specific'][file_name])
        
        return list(set(hidden))  # Remove duplicates
    
    def auto_hide_columns(self, df: pd.DataFrame, file_name: str = None) -> pd.DataFrame:
        """
        Automatically hide columns based on patterns and preferences.
        
        Args:
            df: DataFrame to process
            file_name: Optional file name for file-specific preferences
            
        Returns:
            DataFrame with columns hidden
        """
        original_columns = set(df.columns)
        columns_to_hide = set()
        
        # 1. Hide empty columns above threshold
        empty_threshold = self.preferences['auto_hide_empty_threshold']
        for col in df.columns:
            if df[col].isnull().sum() / len(df) >= empty_threshold:
                columns_to_hide.add(col)
        
        # 2. Hide columns matching patterns
        import re
        for pattern in self.preferences['auto_hide_patterns']:
            for col in df.columns:
                if re.match(pattern, col, re.IGNORECASE):
                    columns_to_hide.add(col)
        
        # 3. Hide previously hidden columns
        previously_hidden = self.get_hidden_columns(file_name)
        columns_to_hide.update(previously_hidden)
        
        # 4. Don't hide always-show columns
        always_show = set(self.preferences['always_show_columns'])
        columns_to_hide = columns_to_hide - always_show
        
        # 5. Apply hiding
        if columns_to_hide:
            df = df.drop(columns=list(columns_to_hide))
            logger.info(f"Auto-hid {len(columns_to_hide)} columns: {list(columns_to_hide)}")
            
            # Save newly hidden columns
            newly_hidden = list(columns_to_hide - set(previously_hidden))
            if newly_hidden:
                self.add_hidden_columns(newly_hidden, file_name)
        
        return df
    
    def manually_hide_columns(self, df: pd.DataFrame, columns: List[str], file_name: str = None) -> pd.DataFrame:
        """
        Manually hide specific columns and save preference.
        
        Args:
            df: DataFrame to process
            columns: List of column names to hide
            file_name: Optional file name for file-specific hiding
            
        Returns:
            DataFrame with specified columns hidden
        """
        # Add to hidden list
        self.add_hidden_columns(columns, file_name)
        
        # Hide columns
        available_columns = [col for col in columns if col in df.columns]
        if available_columns:
            df = df.drop(columns=available_columns)
            logger.info(f"Manually hid {len(available_columns)} columns: {available_columns}")
        
        return df
    
    def show_all_columns(self, df: pd.DataFrame, file_name: str = None) -> pd.DataFrame:
        """
        Show all columns (load original data without hiding).
        
        Args:
            df: DataFrame to process
            file_name: Optional file name
            
        Returns:
            DataFrame with all columns visible
        """
        # This would require keeping the original data
        # For now, just return the current DataFrame
        logger.info("Showing all columns (no hiding applied)")
        return df
    
    def get_column_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get statistics about columns for UI display.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with column statistics
        """
        stats = {
            'total_columns': len(df.columns),
            'empty_columns': [],
            'pattern_matches': [],
            'previously_hidden': [],
            'recommended_hide': []
        }
        
        # Find empty columns
        empty_threshold = self.preferences['auto_hide_empty_threshold']
        for col in df.columns:
            if df[col].isnull().sum() / len(df) >= empty_threshold:
                stats['empty_columns'].append(col)
        
        # Find pattern matches
        import re
        for pattern in self.preferences['auto_hide_patterns']:
            for col in df.columns:
                if re.match(pattern, col, re.IGNORECASE):
                    stats['pattern_matches'].append(col)
        
        # Find previously hidden columns
        stats['previously_hidden'] = [col for col in self.get_hidden_columns() if col in df.columns]
        
        # Recommend columns to hide
        stats['recommended_hide'] = list(set(
            stats['empty_columns'] + 
            stats['pattern_matches'] + 
            stats['previously_hidden']
        ))
        
        return stats
    
    def reset_preferences(self, file_name: str = None):
        """Reset preferences for a file or globally."""
        if file_name:
            if file_name in self.hidden_columns['file_specific']:
                del self.hidden_columns['file_specific'][file_name]
                logger.info(f"Reset preferences for file: {file_name}")
        else:
            self.hidden_columns['global_hidden'] = []
            self.hidden_columns['file_specific'] = {}
            logger.info("Reset all column preferences")
        
        self._save_hidden_columns()


# Global instance
column_preferences = ColumnPreferences()


def auto_hide_columns(df: pd.DataFrame, file_name: str = None) -> pd.DataFrame:
    """Convenience function to auto-hide columns."""
    return column_preferences.auto_hide_columns(df, file_name)


def manually_hide_columns(df: pd.DataFrame, columns: List[str], file_name: str = None) -> pd.DataFrame:
    """Convenience function to manually hide columns."""
    return column_preferences.manually_hide_columns(df, columns, file_name)


def get_column_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Convenience function to get column statistics."""
    return column_preferences.get_column_stats(df)


if __name__ == "__main__":
    # Test the column preferences system
    import pandas as pd
    
    # Create test data
    test_data = {
        'First Name': ['John', 'Jane', 'Bob'],
        'Last Name': ['Smith', 'Doe', 'Johnson'],
        'Property address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
        'Unnamed: 0': [0, 1, 2],
        'temp_col': ['a', 'b', 'c'],
        'Empty Column': [None, None, None],
        'Phone': ['555-1234', '555-5678', '555-9012']
    }
    
    df = pd.DataFrame(test_data)
    
    print("🧪 TESTING COLUMN PREFERENCES")
    print("=" * 40)
    
    print(f"Original columns: {list(df.columns)}")
    
    # Test auto-hiding
    df_cleaned = auto_hide_columns(df, "test_file.csv")
    print(f"After auto-hide: {list(df_cleaned.columns)}")
    
    # Test manual hiding
    df_manual = manually_hide_columns(df_cleaned, ['Phone'], "test_file.csv")
    print(f"After manual hide: {list(df_manual.columns)}")
    
    # Test stats
    stats = get_column_stats(df)
    print(f"Column stats: {stats}")
    
    print("\n✅ Column preferences system ready!") 