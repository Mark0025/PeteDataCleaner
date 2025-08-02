"""
Startup Menu Component

Main menu component displaying available application options.
"""

from typing import List, Tuple, Optional, Callable
from PyQt5.QtWidgets import QLabel, QPushButton
from frontend.components.base_component import BaseComponent
from frontend.utils.logo_utils import create_logo_label
from frontend.constants import CLI_OPTIONS

class StartupMenu(BaseComponent):
    """
    Main menu component showing available application options.
    
    Extends BaseComponent to provide a consistent menu interface
    with logo and navigation support.
    """
    
    def __init__(self, parent=None, on_select: Optional[Callable] = None, 
                 options: Optional[List[Tuple[str, str]]] = None):
        """
        Initialize startup menu.
        
        Args:
            parent: Parent widget
            on_select: Callback function for menu item selection
            options: List of (name, description) tuples for menu items
        """
        super().__init__(parent, show_logo=True, show_navigation=False)
        
        self.on_select = on_select
        self.options = options or CLI_OPTIONS
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Title
        title_label = QLabel('Pete Main Menu')
        title_label.setStyleSheet('font-weight: bold; font-size: 18px;')
        self.layout.addWidget(title_label)
        
        # Create buttons for each option
        self.buttons = []
        for name, desc in self.options:
            btn = QPushButton(f"{name} - {desc}")
            btn.clicked.connect(lambda checked, n=name: self.handle_select(n))
            self.layout.addWidget(btn)
            self.buttons.append(btn)
    
    def handle_select(self, name: str):
        """Handle menu item selection."""
        if self.on_select:
            self.on_select(name)
    
    def update_options(self, options: List[Tuple[str, str]]):
        """Update menu options dynamically."""
        # Clear existing buttons
        for btn in self.buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        
        self.buttons.clear()
        self.options = options
        
        # Recreate buttons
        for name, desc in self.options:
            btn = QPushButton(f"{name} - {desc}")
            btn.clicked.connect(lambda checked, n=name: self.handle_select(n))
            self.layout.addWidget(btn)
            self.buttons.append(btn)