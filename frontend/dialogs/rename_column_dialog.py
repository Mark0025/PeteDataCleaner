"""
Rename Column Dialog

Simple dialog for renaming a single column with validation.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QDialogButtonBox, QMessageBox
)

class RenameColumnDialog(QDialog):
    """
    Dialog for renaming a single column.
    
    Provides a simple interface to change a column name with validation
    to ensure the new name is not empty.
    """
    
    def __init__(self, current_name: str, parent=None):
        """
        Initialize rename column dialog.
        
        Args:
            current_name: Current name of the column to rename
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle('Rename Column')
        self.setModal(True)
        
        self.current_name = current_name
        self.new_name = current_name
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Current name display
        current_layout = QHBoxLayout()
        current_label = QLabel('Current Name:')
        current_name_display = QLabel(self.current_name)
        current_name_display.setStyleSheet('font-weight: bold;')
        current_layout.addWidget(current_label)
        current_layout.addWidget(current_name_display)
        layout.addLayout(current_layout)
        
        # New name input
        new_name_layout = QHBoxLayout()
        new_name_label = QLabel('New Name:')
        self.new_name_input = QLineEdit(self.current_name)
        self.new_name_input.selectAll()  # Select all text for easy editing
        new_name_layout.addWidget(new_name_label)
        new_name_layout.addWidget(self.new_name_input)
        layout.addLayout(new_name_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Focus on input field
        self.new_name_input.setFocus()
    
    def validate_and_accept(self):
        """Validate the new name and accept the dialog."""
        new_name = self.new_name_input.text().strip()
        
        # Ensure new name is not empty
        if not new_name:
            QMessageBox.warning(
                self, 
                'Invalid Name', 
                'New column name cannot be empty.'
            )
            return
        
        # Ensure name has actually changed
        if new_name == self.current_name:
            QMessageBox.information(
                self,
                'No Change',
                'The new name is the same as the current name.'
            )
            return
        
        self.new_name = new_name
        self.accept()
    
    def get_new_name(self) -> str:
        """Get the new column name after dialog completion."""
        return self.new_name