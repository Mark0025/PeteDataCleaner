"""
Main Window Module

The main application window that orchestrates the entire frontend.
"""

import os
import sys
import pandas as pd
from loguru import logger

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QToolButton, QMessageBox, QDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Import local modules
from frontend.constants import CLI_OPTIONS, DEFAULT_RULES_CONFIG
from frontend.utils.logo_utils import create_logo_label

# Import backend components
from backend.utils.data_standardizer import DataStandardizer
from backend.sheets_client import SheetsClient

# Import modular frontend components
from frontend.components import (
    StartupMenu, FileSelector, DataPrepEditor, MappingUI, StandardizedPreviewUI
)
from frontend.toolsui import DataToolsPanel
from frontend.dialogs import SettingsDialog

class MainWindow(QMainWindow):
    """
    Main application window.
    
    Orchestrates all frontend components and manages navigation
    between different views (menu, file selection, mapping, preview).
    """
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowTitle('Pete GUI Mapping Tool')
        self.resize(1200, 800)
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Application state
        self.current_df = None
        self.current_pete_headers = None
        self.current_mapping = None
        self.rules_config = DEFAULT_RULES_CONFIG.copy()
        
        # Menu options configuration
        self.menu_options = {
            'Workspace': ("Workspace", True),
            'Standardize': ("Standardize", True),
            'Rules': ("Rules", True),
            'Backend': ("Backend", True),
            'Test': ("Test", True),
            'GUI Mapping Tool': ("GUI Mapping Tool", True),
            'Exit': ("Exit", True)
        }
        
        # Setup UI
        self._setup_ui()
        
        # Show initial view
        self.show_startup_menu()
    
    def _setup_ui(self):
        """Setup the main UI components."""
        # Logo
        self.layout.addWidget(create_logo_label())
        
        # Settings button (always available)
        self.settings_btn = QToolButton()
        self.settings_btn.setIcon(QIcon.fromTheme('preferences-system'))
        self.settings_btn.setToolTip('Settings')
        self.settings_btn.clicked.connect(self.open_settings)
        self.layout.addWidget(self.settings_btn, alignment=Qt.AlignRight)
    
    def clear_layout(self, keep_logo_and_settings=True):
        """Clear the layout while optionally preserving logo and settings."""
        widgets_to_remove = []
        
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                
                # Keep logo and settings if requested
                if keep_logo_and_settings and (
                    widget == self.settings_btn or 
                    'logo' in widget.objectName().lower() if widget.objectName() else False
                ):
                    continue
                
                widgets_to_remove.append(widget)
        
        # Remove widgets
        for widget in widgets_to_remove:
            self.layout.removeWidget(widget)
            widget.deleteLater()
    
    def show_startup_menu(self):
        """Show the main startup menu."""
        self.clear_layout()
        
        # Create visible options based on menu configuration
        visible_options = [
            (key, desc) for key, (desc, visible) in self.menu_options.items() 
            if visible
        ]
        
        self.startup_menu = StartupMenu(
            parent=self,
            on_select=self.handle_menu_select,
            options=visible_options
        )
        self.layout.addWidget(self.startup_menu)
    
    def show_file_selector(self):
        """Show the file selection interface."""
        self.clear_layout()
        
        self.file_selector = FileSelector(
            parent=self,
            on_mapping_request=self.show_data_tools_panel,  # Go directly to tools panel
            on_back=self.show_startup_menu,
            on_exit=self.close
        )
        self.layout.addWidget(self.file_selector)
    
    def show_data_tools_panel(self, df: pd.DataFrame, pete_headers: list):
        """Show the data tools panel immediately after upload."""
        self.clear_layout()
        
        # Store Pete headers for later use
        self.current_pete_headers = pete_headers
        
        # Detect data source from filename or content
        data_source = self._detect_data_source(df)
        
        self.data_tools_panel = DataToolsPanel(
            parent=self,
            df=df,
            data_source=data_source,
            on_back=self.show_file_selector,
            on_proceed=self._proceed_from_tools_to_pete
        )
        self.layout.addWidget(self.data_tools_panel)
    
    def _detect_data_source(self, df: pd.DataFrame) -> str:
        """Detect the data source based on column patterns."""
        columns = [col.lower() for col in df.columns]
        
        # Check for REISIFT patterns  
        reisift_indicators = ['mls', 'deed', 'foreclosure date', 'property taxes', 'exported from reisift.io']
        if any(indicator in ' '.join(columns) for indicator in reisift_indicators):
            return "REISIFT"
        
        # Check for other known sources
        # TODO: Add other data source patterns
        
        return "Unknown"
    
    def _proceed_from_tools_to_pete(self, prepared_df: pd.DataFrame, mapping_config: dict):
        """Proceed from data tools to Pete mapping."""
        # Store the mapping configuration for the session
        self.current_mapping_config = mapping_config
        self.show_mapping_ui(prepared_df, self.current_pete_headers)
    
    def show_data_prep_editor(self, df: pd.DataFrame, pete_headers: list):
        """Show the data preparation editor before Pete mapping."""
        self.clear_layout()
        
        # Store Pete headers for later use
        self.current_pete_headers = pete_headers
        
        self.data_prep_editor = DataPrepEditor(
            parent=self,
            df=df,
            on_back=self.show_file_selector,
            on_proceed=self.proceed_to_pete_mapping
        )
        self.layout.addWidget(self.data_prep_editor)
    
    def proceed_to_pete_mapping(self, prepared_df: pd.DataFrame):
        """Proceed to Pete mapping with prepared data."""
        self.show_mapping_ui(prepared_df, self.current_pete_headers)
    
    def show_mapping_ui(self, df: pd.DataFrame, pete_headers: list):
        """Show the mapping interface."""
        self.clear_layout()
        
        # Store current data
        self.current_df = df
        self.current_pete_headers = pete_headers
        
        self.mapping_ui = MappingUI(
            parent=self,
            df=df,
            pete_headers=pete_headers,
            rules=self.rules_config,
            on_back=self.return_to_data_prep,
            on_exit=self.close,
            on_settings=self.open_settings
        )
        self.layout.addWidget(self.mapping_ui)
    
    def return_to_data_prep(self):
        """Return to data preparation editor with current data."""
        if hasattr(self, 'current_df') and hasattr(self, 'current_pete_headers'):
            self.show_data_prep_editor(self.current_df, self.current_pete_headers)
        else:
            self.show_file_selector()
    
    def show_standardized_preview(self, df: pd.DataFrame):
        """Show the standardized data preview."""
        self.clear_layout()
        
        self.preview_ui = StandardizedPreviewUI(
            parent=self,
            df=df,
            on_back=self.show_mapping_ui_with_current_data,
            on_exit=self.close
        )
        self.layout.addWidget(self.preview_ui)
    
    def show_mapping_ui_with_current_data(self):
        """Return to mapping UI with current data."""
        if self.current_df is not None and self.current_pete_headers is not None:
            self.show_mapping_ui(self.current_df, self.current_pete_headers)
        else:
            self.show_file_selector()
    
    def handle_menu_select(self, name: str):
        """Handle menu item selection."""
        if name == "GUI Mapping Tool":
            self.show_file_selector()
        elif name == "Exit":
            self.close()
        elif name == "Test":
            self._show_test_interface()
        else:
            QMessageBox.information(
                self, 
                name, 
                f"{name} utility coming soon.\n\nThis feature will be implemented in a future update."
            )
    
    def _show_test_interface(self):
        """Show test interface (placeholder)."""
        QMessageBox.information(
            self,
            "Test Interface",
            "Test interface would run:\n\n"
            "• Backend analysis utilities\n"
            "• Data validation tests\n" 
            "• Mapping rule verification\n"
            "• Performance benchmarks\n\n"
            "Coming soon!"
        )
    
    def open_settings(self):
        """Open the settings dialog."""
        settings_dialog = SettingsDialog(
            parent=self,
            rules=self.rules_config,
            menu_options=self.menu_options,
            on_save=self.apply_settings
        )
        settings_dialog.exec_()
    
    def apply_settings(self, new_rules: dict, new_menu_options: dict):
        """Apply new settings from settings dialog."""
        # Update configuration
        self.rules_config.update(new_rules)
        self.menu_options.update(new_menu_options)
        
        logger.info(f"Settings updated: rules={new_rules}, menu={new_menu_options}")
        
        # Refresh current view to apply changes
        self.show_startup_menu()
    
    def closeEvent(self, event):
        """Handle application close event."""
        reply = QMessageBox.question(
            self,
            'Exit Application',
            'Are you sure you want to exit Pete?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("Application closed by user")
            event.accept()
        else:
            event.ignore()

def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName('Pete GUI Mapping Tool')
    app.setApplicationVersion('2.0')
    app.setOrganizationName('Pete Data Solutions')
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()