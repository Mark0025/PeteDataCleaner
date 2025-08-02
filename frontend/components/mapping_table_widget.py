"""
Mapping Table Widget

Enhanced table widget with multi-select capability and context menu
for column operations like concatenation and renaming.
"""

from typing import List, Optional, Callable
from PyQt5.QtWidgets import (
    QTableWidget, QAbstractItemView, QMenu, QAction, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal

from frontend.dialogs.concatenation_dialog import ConcatenationDialog
from frontend.dialogs.rename_column_dialog import RenameColumnDialog

class MappingTableWidget(QTableWidget):
    """
    Enhanced table widget with multi-select and context menu.
    
    Features:
    - Multi-column selection
    - Right-click context menu
    - Column concatenation and renaming
    - Signals for parent communication
    """
    
    # Signals for parent communication
    columns_concatenation_requested = pyqtSignal(list, str, str)  # source_cols, dest_header, separator
    column_rename_requested = pyqtSignal(str, str)  # old_name, new_name
    
    def __init__(self, parent=None):
        """
        Initialize mapping table widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Configure selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Track selected columns
        self.selected_columns: List[str] = []
        
        # Available Pete headers for concatenation
        self.pete_headers: List[str] = []
    
    def set_pete_headers(self, headers: List[str]):
        """Set available Pete headers for concatenation dialogs."""
        self.pete_headers = headers
    
    def mousePressEvent(self, event):
        """Handle mouse press to update selected columns."""
        super().mousePressEvent(event)
        
        # Update selected columns list
        self.selected_columns = []
        for index in self.selectedIndexes():
            if self.horizontalHeaderItem(index.column()):
                col_name = self.horizontalHeaderItem(index.column()).text()
                if col_name not in self.selected_columns:
                    self.selected_columns.append(col_name)
    
    def show_context_menu(self, pos):
        """Show context menu at the specified position."""
        context_menu = QMenu(self)
        
        # Concatenate action (if 2+ columns selected)
        if len(self.selected_columns) > 1:
            concat_action = QAction('Concatenate Columns', self)
            concat_action.triggered.connect(self.open_concatenation_dialog)
            context_menu.addAction(concat_action)
        
        # Rename action (if 1 column selected)
        if len(self.selected_columns) == 1:
            rename_action = QAction('Rename Column', self)
            rename_action.triggered.connect(self.open_rename_dialog)
            context_menu.addAction(rename_action)
        
        # Show separator if we have actions
        if context_menu.actions():
            context_menu.addSeparator()
        
        # Info action (always available)
        info_action = QAction(f'Selected: {len(self.selected_columns)} columns', self)
        info_action.setEnabled(False)
        context_menu.addAction(info_action)
        
        # Show menu if it has any enabled actions
        if any(action.isEnabled() for action in context_menu.actions()[:-1]):
            context_menu.exec_(self.mapToGlobal(pos))
    
    def open_concatenation_dialog(self):
        """Open dialog for column concatenation."""
        if not self.pete_headers:
            # If no Pete headers available, use empty list
            self.pete_headers = []
        
        dialog = ConcatenationDialog(
            upload_columns=self.selected_columns,
            pete_headers=self.pete_headers,
            pre_selected_columns=self.selected_columns,
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted and dialog.result:
            result = dialog.result
            self.columns_concatenation_requested.emit(
                result['source_columns'],
                result['destination_header'],
                result['separator']
            )
    
    def open_rename_dialog(self):
        """Open dialog for column renaming."""
        if not self.selected_columns:
            return
        
        current_name = self.selected_columns[0]
        dialog = RenameColumnDialog(current_name, parent=self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.get_new_name()
            if new_name != current_name:
                self.column_rename_requested.emit(current_name, new_name)
    
    def get_selected_columns(self) -> List[str]:
        """Get currently selected column names."""
        return self.selected_columns.copy()
    
    def clear_selection_tracking(self):
        """Clear the selected columns tracking."""
        self.selected_columns = []