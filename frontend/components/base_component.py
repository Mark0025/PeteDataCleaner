from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from frontend.utils.logo_utils import create_logo_label

class BaseComponent(QWidget):
    """
    Base component with common UI methods and layout management.
    """
    def __init__(self, parent=None, show_logo=True, show_navigation=False, 
                 on_back=None, on_exit=None):
        """
        Initialize the base component.
        
        :param parent: Parent widget
        :param show_logo: Whether to show the Pete logo
        :param show_navigation: Whether to show navigation buttons
        :param on_back: Callback for back button
        :param on_exit: Callback for exit button
        """
        super().__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Add logo if requested
        if show_logo:
            self.layout.addWidget(create_logo_label())
        
        # Store navigation callbacks
        self.on_back = on_back
        self.on_exit = on_exit
        
        # Add navigation buttons if requested
        if show_navigation:
            self._add_navigation_buttons()
    
    def _add_navigation_buttons(self):
        """
        Add back and exit buttons to the layout.
        """
        nav_layout = QHBoxLayout()
        
        # Back button
        if self.on_back:
            self.back_btn = QPushButton('Back to Main Menu')
            self.back_btn.clicked.connect(self._handle_back)
            nav_layout.addWidget(self.back_btn)
        
        # Exit button
        if self.on_exit:
            self.exit_btn = QPushButton('Exit')
            self.exit_btn.clicked.connect(self._handle_exit)
            nav_layout.addWidget(self.exit_btn)
        
        # Add navigation layout to main layout
        self.layout.addLayout(nav_layout)
    
    def _handle_back(self):
        """
        Handle back button click.
        """
        if self.on_back:
            self.on_back()
    
    def _handle_exit(self):
        """
        Handle exit button click.
        """
        if self.on_exit:
            self.on_exit() 