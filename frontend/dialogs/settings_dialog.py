"""
Settings Dialog

Dialog for configuring application settings including mapping rules,
preview options, and menu visibility.
"""

from typing import Dict, Any, Optional, Callable
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QCheckBox, QDialogButtonBox, 
    QDoubleSpinBox, QLabel
)

class SettingsDialog(QDialog):
    """
    Settings configuration dialog.
    
    Allows users to configure:
    - Fuzzy matching parameters
    - Preview table settings
    - Empty column filtering
    - Menu option visibility
    """
    
    def __init__(self, parent=None, rules: Optional[Dict[str, Any]] = None, 
                 menu_options: Optional[Dict[str, tuple]] = None, 
                 on_save: Optional[Callable] = None):
        """
        Initialize settings dialog.
        
        Args:
            parent: Parent widget
            rules: Current mapping rules configuration
            menu_options: Menu options configuration
            on_save: Callback for saving settings
        """
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.setModal(True)
        
        self.rules = rules or {}
        self.menu_options = menu_options or {}
        self.on_save = on_save
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QFormLayout(self)
        
        # Mapping/preview settings
        self._setup_mapping_settings(layout)
        
        # Empty column filtering settings
        self._setup_empty_column_settings(layout)
        
        # Menu options toggles
        self._setup_menu_options(layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _setup_mapping_settings(self, layout: QFormLayout):
        """Setup mapping and preview settings."""
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
    
    def _setup_empty_column_settings(self, layout: QFormLayout):
        """Setup empty column filtering settings."""
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
    
    def _setup_menu_options(self, layout: QFormLayout):
        """Setup menu options toggles."""
        layout.addRow(QLabel('<b>Menu Options</b>'))
        self.menu_checkboxes = {}
        
        for key, (label, visible) in self.menu_options.items():
            cb = QCheckBox(f'Show "{label}" on main menu')
            cb.setChecked(visible)
            self.menu_checkboxes[key] = cb
            layout.addRow(cb)
    
    def save(self):
        """Save settings and close dialog."""
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
        menu_opts = {
            k: (lbl, self.menu_checkboxes[k].isChecked()) 
            for k, (lbl, _) in self.menu_options.items()
        }
        
        if self.on_save:
            self.on_save(self.rules, menu_opts)
        
        self.accept()