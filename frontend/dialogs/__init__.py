"""
Frontend Dialogs Package

This package contains specialized dialog windows for the Pete frontend application.

Available dialogs:
- SettingsDialog: Application settings configuration
- RuleMappingDialog: Dynamic mapping rules editor
- ConcatenationDialog: Column concatenation dialog
- RenameColumnDialog: Column renaming dialog
- DuplicateRemovalDialog: Duplicate row removal configuration
"""

from .settings_dialog import SettingsDialog
from .rule_mapping_dialog import RuleMappingDialog
from .concatenation_dialog import ConcatenationDialog
from .rename_column_dialog import RenameColumnDialog
from .duplicate_removal_dialog import DuplicateRemovalDialog

__all__ = [
    'SettingsDialog',
    'RuleMappingDialog', 
    'ConcatenationDialog',
    'RenameColumnDialog',
    'DuplicateRemovalDialog'
]