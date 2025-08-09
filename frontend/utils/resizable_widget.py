#!/usr/bin/env python3
"""
Resizable Widget Utility

Provides a reusable resizable widget with QSplitter and white borders
for consistent UI across the application.
"""

from PyQt5.QtWidgets import (
    QWidget, QSplitter, QVBoxLayout, QHBoxLayout, 
    QFrame, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import Optional, Union, Tuple


class ResizableWidget(QWidget):
    """
    Reusable resizable widget with QSplitter and white borders.
    
    Features:
    - Horizontal or vertical splitter
    - White borders around frames
    - Dynamic resizing
    - Optional titles for each section
    - Consistent styling across the app
    """
    
    # Signal emitted when splitter position changes
    splitter_moved = pyqtSignal(int, int)  # left_size, right_size
    
    def __init__(
        self, 
        left_widget: QWidget, 
        right_widget: QWidget,
        orientation: Qt.Orientation = Qt.Horizontal,
        left_title: Optional[str] = None,
        right_title: Optional[str] = None,
        initial_split: Tuple[int, int] = (1, 1),
        parent: Optional[QWidget] = None
    ):
        """
        Initialize resizable widget.
        
        Args:
            left_widget: Left/top widget
            right_widget: Right/bottom widget
            orientation: Splitter orientation (Horizontal/Vertical)
            left_title: Optional title for left section
            right_title: Optional title for right section
            initial_split: Initial size ratio (left, right)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.left_widget = left_widget
        self.right_widget = right_widget
        self.orientation = orientation
        self.left_title = left_title
        self.right_title = right_title
        self.initial_split = initial_split
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create splitter
        self.splitter = QSplitter(self.orientation)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(4)
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
        
        # Create left frame with optional title
        self.left_frame = self._create_section_frame(
            self.left_widget, 
            self.left_title, 
            "left"
        )
        
        # Create right frame with optional title
        self.right_frame = self._create_section_frame(
            self.right_widget, 
            self.right_title, 
            "right"
        )
        
        # Add frames to splitter
        self.splitter.addWidget(self.left_frame)
        self.splitter.addWidget(self.right_frame)
        
        # Set initial sizes
        total_size = 100
        left_size = int(total_size * self.initial_split[0] / sum(self.initial_split))
        right_size = total_size - left_size
        self.splitter.setSizes([left_size, right_size])
        
        layout.addWidget(self.splitter)
    
    def _create_section_frame(
        self, 
        content_widget: QWidget, 
        title: Optional[str], 
        section_name: str
    ) -> QFrame:
        """Create a section frame with optional title."""
        frame = QFrame()
        frame.setObjectName(f"{section_name}_section_frame")
        frame.setFrameStyle(QFrame.Box)
        frame.setLineWidth(1)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Add title if provided
        if title:
            title_label = QLabel(title)
            title_label.setObjectName(f"{section_name}_section_title")
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 14px;
                    color: #333;
                    background-color: #f8f9fa;
                    padding: 6px;
                    border-radius: 4px;
                    margin-bottom: 4px;
                }
            """)
            layout.addWidget(title_label)
        
        # Add content widget
        content_widget.setParent(frame)
        layout.addWidget(content_widget)
        
        return frame
    
    def _apply_styling(self):
        """Apply consistent styling."""
        self.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
            }
            QSplitter::handle:hover {
                background-color: #d0d0d0;
            }
            QSplitter::handle:pressed {
                background-color: #c0c0c0;
            }
            
            QFrame#left_section_frame,
            QFrame#right_section_frame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
            }
            
            QFrame#left_section_frame:hover,
            QFrame#right_section_frame:hover {
                border-color: #d0d0d0;
            }
        """)
    
    def _on_splitter_moved(self, pos: int, index: int):
        """Handle splitter movement."""
        sizes = self.splitter.sizes()
        if len(sizes) >= 2:
            self.splitter_moved.emit(sizes[0], sizes[1])
    
    def get_splitter_sizes(self) -> Tuple[int, int]:
        """Get current splitter sizes."""
        sizes = self.splitter.sizes()
        return (sizes[0], sizes[1]) if len(sizes) >= 2 else (50, 50)
    
    def set_splitter_sizes(self, left_size: int, right_size: int):
        """Set splitter sizes."""
        self.splitter.setSizes([left_size, right_size])
    
    def set_splitter_ratio(self, left_ratio: float, right_ratio: float):
        """Set splitter ratio (0.0 to 1.0)."""
        total = left_ratio + right_ratio
        if total > 0:
            left_size = int(left_ratio / total * 100)
            right_size = 100 - left_size
            self.set_splitter_sizes(left_size, right_size)


class ResizablePanel(ResizableWidget):
    """
    Specialized resizable panel for tool panels.
    
    Provides a consistent interface for tool panels with
    resizable sections and proper styling.
    """
    
    def __init__(
        self,
        tools_widget: QWidget,
        content_widget: QWidget,
        tools_title: str = "Tools",
        content_title: str = "Content",
        tools_width_ratio: float = 0.3,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize resizable panel.
        
        Args:
            tools_widget: Tools/controls widget
            content_widget: Main content widget
            tools_title: Title for tools section
            content_title: Title for content section
            tools_width_ratio: Initial width ratio for tools (0.0 to 1.0)
            parent: Parent widget
        """
        content_ratio = 1.0 - tools_width_ratio
        super().__init__(
            left_widget=tools_widget,
            right_widget=content_widget,
            orientation=Qt.Horizontal,
            left_title=tools_title,
            right_title=content_title,
            initial_split=(tools_width_ratio, content_ratio),
            parent=parent
        )
    
    def _apply_styling(self):
        """Apply specialized styling for tool panels."""
        super()._apply_styling()
        
        # Add additional styling for tool panels
        additional_style = """
            QFrame#left_section_frame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                min-width: 200px;
                max-width: 400px;
            }
            
            QFrame#right_section_frame {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                min-width: 300px;
            }
        """
        
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + additional_style)


# Convenience functions for easy integration
def create_resizable_panel(
    left_widget: QWidget,
    right_widget: QWidget,
    left_title: Optional[str] = None,
    right_title: Optional[str] = None,
    orientation: Qt.Orientation = Qt.Horizontal
) -> ResizableWidget:
    """Create a resizable panel with the given widgets."""
    return ResizableWidget(
        left_widget=left_widget,
        right_widget=right_widget,
        orientation=orientation,
        left_title=left_title,
        right_title=right_title
    )


def create_tools_panel(
    tools_widget: QWidget,
    content_widget: QWidget,
    tools_title: str = "Tools",
    content_title: str = "Content"
) -> ResizablePanel:
    """Create a specialized tools panel."""
    return ResizablePanel(
        tools_widget=tools_widget,
        content_widget=content_widget,
        tools_title=tools_title,
        content_title=content_title
    )


if __name__ == "__main__":
    # Test the resizable widget
    from PyQt5.QtWidgets import QApplication, QTextEdit, QPushButton, QVBoxLayout
    import sys
    
    app = QApplication(sys.argv)
    
    # Create test widgets
    left_widget = QTextEdit()
    left_widget.setPlainText("Left Widget Content")
    
    right_widget = QTextEdit()
    right_widget.setPlainText("Right Widget Content")
    
    # Create resizable widget
    resizable = create_resizable_panel(
        left_widget=left_widget,
        right_widget=right_widget,
        left_title="Left Section",
        right_title="Right Section"
    )
    
    resizable.resize(800, 600)
    resizable.show()
    
    sys.exit(app.exec_()) 