"""
Data Version Manager

Handles version history and undo/redo functionality for data preparation.
"""

import pandas as pd
from typing import Dict, List, Any, Optional


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
    
    def get_summary(self) -> Dict[str, Any]:
        """Get version summary statistics."""
        return {
            'total_versions': len(self.versions),
            'current_version': self.current_version + 1 if self.current_version >= 0 else 0,
            'changes_made': len(self.versions) - 1,  # Subtract initial version
            'can_undo': self.can_undo(),
            'can_redo': self.can_redo()
        }