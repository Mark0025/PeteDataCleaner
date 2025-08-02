"""
Smart Concatenation Dialog

Enhanced dialog for merging multiple columns with intelligent suggestions.
"""

from typing import Dict, List, Any, Optional
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QListWidget, QComboBox, 
    QCheckBox, QMessageBox, QInputDialog, QGroupBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt


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
        self.delimiter_combo.setCurrentText('Space')  # Default to space, not comma+space
        self.delimiter_combo.currentTextChanged.connect(self._on_delimiter_changed)
        delimiter_layout.addWidget(self.delimiter_combo)
        
        # Dynamic preview label
        self.preview_label = QLabel()
        self._update_delimiter_preview()
        self.delimiter_combo.currentTextChanged.connect(self._update_delimiter_preview)
        delimiter_layout.addWidget(self.preview_label)
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
        
        self.include_headers = QCheckBox('Include field headers in output')
        self.include_headers.setChecked(False)
        self.include_headers.setToolTip('Prefix each value with its column name (e.g., "Name: John Doe")')
        self.include_headers.toggled.connect(self._update_delimiter_preview)
        options_layout.addWidget(self.include_headers)
        
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
    
    def _update_delimiter_preview(self):
        """Update the delimiter preview to show what will actually happen."""
        delimiter_name = self.delimiter_combo.currentText()
        if delimiter_name == 'Custom':
            delimiter = getattr(self, 'custom_delimiter_text', ', ')
        else:
            delimiter = self.DELIMITERS.get(delimiter_name, ' ')
        
        # Check if include headers is enabled
        include_headers = getattr(self, 'include_headers', None) and self.include_headers.isChecked()
        
        # Create preview based on number of columns and settings
        if len(self.selected_columns) == 2:
            col1, col2 = self.selected_columns[:2]
            if include_headers:
                # Show with headers
                if delimiter == ' | ':
                    preview = f'Preview: "{col1}: John | {col2}: Doe"'
                elif delimiter == ', ':
                    preview = f'Preview: "{col1}: John, {col2}: Doe"'
                else:
                    preview = f'Preview: "{col1}: John{delimiter}{col2}: Doe"'
            else:
                # Show without headers (original logic)
                if delimiter == ' ':
                    preview = 'Preview: "John" + "Doe" → "John Doe"'
                elif delimiter == ', ':
                    preview = 'Preview: "John" + "Doe" → "John, Doe"'
                elif delimiter == '; ':
                    preview = 'Preview: "John" + "Doe" → "John; Doe"'
                elif delimiter == ' | ':
                    preview = 'Preview: "John" + "Doe" → "John | Doe"'
                elif delimiter == '\n':
                    preview = 'Preview: "John" + "Doe" → "John\\nDoe"'
                elif delimiter == ',':
                    preview = 'Preview: "John" + "Doe" → "John,Doe"'
                elif delimiter == ' - ':
                    preview = 'Preview: "John" + "Doe" → "John - Doe"'
                elif delimiter == '_':
                    preview = 'Preview: "John" + "Doe" → "John_Doe"'
                elif delimiter == '|':
                    preview = 'Preview: "John" + "Doe" → "John|Doe"'
                else:
                    preview = f'Preview: "John" + "Doe" → "John{delimiter}Doe"'
        
        elif len(self.selected_columns) >= 3:
            # Show multi-column example
            if include_headers:
                cols = self.selected_columns[:3]
                if delimiter == ' | ':
                    preview = f'Preview: "{cols[0]}: John | {cols[1]}: Doe | {cols[2]}: ABC Corp"'
                elif delimiter == ', ':
                    preview = f'Preview: "{cols[0]}: John, {cols[1]}: Doe, {cols[2]}: ABC Corp"'
                else:
                    preview = f'Preview: "{cols[0]}: John{delimiter}{cols[1]}: Doe{delimiter}{cols[2]}: ABC Corp"'
            else:
                if delimiter == ' | ':
                    preview = 'Preview: "John | Doe | ABC Corp"'
                elif delimiter == ', ':
                    preview = 'Preview: "John, Doe, ABC Corp"'
                else:
                    preview = f'Preview: "John{delimiter}Doe{delimiter}ABC Corp"'
        
        else:
            preview = 'Preview: Select columns to see preview'
        
        self.preview_label.setText(preview)
        self.preview_label.setStyleSheet('color: #666; font-style: italic;')
    
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
                self._update_delimiter_preview()
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
            delimiter = getattr(self, 'custom_delimiter_text', ', ')
        else:
            delimiter = self.DELIMITERS[delimiter_name]
        
        self.result = {
            'columns': self.selected_columns,
            'new_name': new_name,
            'delimiter': delimiter,
            'keep_original': self.keep_original.isChecked(),
            'handle_empty': self.handle_empty.isChecked(),
            'include_headers': self.include_headers.isChecked()
        }
        
        self.accept()
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """Get the merge configuration result."""
        return self.result