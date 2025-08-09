#!/usr/bin/env python3
"""
Progress Dialog

Shows real-time progress for long-running operations with detailed status updates.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, 
    QPushButton, QTextEdit, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from typing import Optional, Callable
from loguru import logger


class ProgressDialog(QDialog):
    """
    Progress dialog with real-time updates and detailed status.
    
    Features:
    - Real-time progress bar
    - Detailed status messages
    - ETA and speed information
    - Cancel button
    - Auto-close on completion
    """
    
    # Signal emitted when operation completes
    completed = pyqtSignal()
    
    def __init__(self, title: str = "Processing", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 300)
        
        # Setup UI
        self._setup_ui()
        
        # State
        self.is_cancelled = False
        self.operation_complete = False
        
        # Timer for updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_progress)
        self.update_timer.start(100)  # Update every 100ms
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Processing Data")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #667eea; margin: 10px;")
        layout.addWidget(title_label)
        
        # Current operation
        self.operation_label = QLabel("Initializing...")
        self.operation_label.setFont(QFont("Arial", 12))
        self.operation_label.setStyleSheet("color: #333; margin: 5px;")
        layout.addWidget(self.operation_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #667eea;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status details
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.Box)
        details_frame.setStyleSheet("border: 1px solid #ddd; border-radius: 5px; padding: 10px;")
        details_layout = QVBoxLayout(details_frame)
        
        # Progress details
        self.progress_label = QLabel("0% complete")
        self.progress_label.setStyleSheet("color: #666;")
        details_layout.addWidget(self.progress_label)
        
        # Speed and ETA
        self.speed_label = QLabel("")
        self.speed_label.setStyleSheet("color: #666;")
        details_layout.addWidget(self.speed_label)
        
        # ETA
        self.eta_label = QLabel("")
        self.eta_label.setStyleSheet("color: #666;")
        details_layout.addWidget(self.eta_label)
        
        layout.addWidget(details_frame)
        
        # Log output
        log_label = QLabel("Recent Activity:")
        log_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: #f8f9fa;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel_operation)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setVisible(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def update_operation(self, operation: str, progress: int = None, 
                        details: str = None, speed: str = None, eta: str = None):
        """
        Update the progress dialog with new information.
        
        Args:
            operation: Current operation name
            progress: Progress percentage (0-100)
            details: Additional details
            speed: Processing speed (e.g., "1000 records/sec")
            eta: Estimated time to completion
        """
        # Update operation
        if operation:
            self.operation_label.setText(operation)
        
        # Update progress
        if progress is not None:
            self.progress_bar.setValue(progress)
            self.progress_label.setText(f"{progress}% complete")
        
        # Update details
        if details:
            self.progress_label.setText(f"{progress}% complete - {details}")
        
        # Update speed
        if speed:
            self.speed_label.setText(f"Speed: {speed}")
        
        # Update ETA
        if eta:
            self.eta_label.setText(f"ETA: {eta}")
        
        # Add to log
        if operation:
            self.log_text.append(f"[{self._get_timestamp()}] {operation}")
            # Auto-scroll to bottom
            self.log_text.verticalScrollBar().setValue(
                self.log_text.verticalScrollBar().maximum()
            )
    
    def add_log_message(self, message: str):
        """Add a message to the log."""
        self.log_text.append(f"[{self._get_timestamp()}] {message}")
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def complete_operation(self, success: bool = True, message: str = None):
        """
        Mark the operation as complete.
        
        Args:
            success: Whether the operation completed successfully
            message: Completion message
        """
        self.operation_complete = True
        
        if success:
            self.progress_bar.setValue(100)
            self.operation_label.setText("✅ Operation Complete")
            self.operation_label.setStyleSheet("color: #28a745; font-weight: bold;")
            
            if message:
                self.add_log_message(f"✅ {message}")
            else:
                self.add_log_message("✅ Operation completed successfully")
        else:
            self.operation_label.setText("❌ Operation Failed")
            self.operation_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            
            if message:
                self.add_log_message(f"❌ {message}")
            else:
                self.add_log_message("❌ Operation failed")
        
        # Show close button, hide cancel button
        self.cancel_btn.setVisible(False)
        self.close_btn.setVisible(True)
        
        # Emit completion signal
        self.completed.emit()
    
    def cancel_operation(self):
        """Cancel the current operation."""
        self.is_cancelled = True
        self.operation_label.setText("⏹️ Cancelling...")
        self.operation_label.setStyleSheet("color: #ffc107; font-weight: bold;")
        self.add_log_message("⏹️ Operation cancelled by user")
        
        # Show close button, hide cancel button
        self.cancel_btn.setVisible(False)
        self.close_btn.setVisible(True)
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self.is_cancelled
    
    def _update_progress(self):
        """Update progress display (called by timer)."""
        # This can be overridden for custom progress updates
        pass
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for log messages."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if not self.operation_complete and not self.is_cancelled:
            # Ask user if they want to cancel
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, 
                "Cancel Operation", 
                "Operation is still running. Do you want to cancel?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.cancel_operation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class OwnerAnalysisProgressDialog(ProgressDialog):
    """
    Specialized progress dialog for owner analysis operations.
    """
    
    def __init__(self, parent=None):
        super().__init__("Owner Analysis", parent)
        
        # Override title
        title_label = self.findChild(QLabel)
        if title_label:
            title_label.setText("🏠 Owner Analysis")
        
        # Add owner analysis specific fields
        self._add_owner_analysis_fields()
    
    def _add_owner_analysis_fields(self):
        """Add owner analysis specific fields."""
        # Find the details frame
        details_frame = None
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item.widget() and isinstance(item.widget(), QFrame):
                details_frame = item.widget()
                break
        
        if details_frame:
            details_layout = details_frame.layout()
            
            # Add owner analysis specific labels
            self.owners_label = QLabel("Owners found: 0")
            self.owners_label.setStyleSheet("color: #666;")
            details_layout.addWidget(self.owners_label)
            
            self.businesses_label = QLabel("Business entities: 0")
            self.businesses_label.setStyleSheet("color: #666;")
            details_layout.addWidget(self.businesses_label)
            
            self.multi_property_label = QLabel("Multi-property owners: 0")
            self.multi_property_label.setStyleSheet("color: #666;")
            details_layout.addWidget(self.multi_property_label)
    
    def update_owner_stats(self, total_owners: int, business_entities: int, multi_property: int):
        """Update owner analysis statistics."""
        self.owners_label.setText(f"Owners found: {total_owners:,}")
        self.businesses_label.setText(f"Business entities: {business_entities:,}")
        self.multi_property_label.setText(f"Multi-property owners: {multi_property:,}")


# Convenience function to show progress for owner analysis
def show_owner_analysis_progress(parent=None) -> OwnerAnalysisProgressDialog:
    """Show owner analysis progress dialog."""
    dialog = OwnerAnalysisProgressDialog(parent)
    dialog.show()
    return dialog


if __name__ == "__main__":
    # Test the progress dialog
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = ProgressDialog("Test Operation")
    dialog.show()
    
    # Simulate progress updates
    import time
    
    def simulate_progress():
        for i in range(0, 101, 10):
            if dialog.is_cancelled:
                break
            
            dialog.update_operation(
                f"Processing step {i//10 + 1}/10",
                i,
                f"Processed {i*100} records",
                f"{1000 + i*50} records/sec",
                f"{10 - i//10} seconds remaining"
            )
            time.sleep(0.5)
        
        dialog.complete_operation(True, "All data processed successfully!")
    
    # Start simulation after a short delay
    from PyQt5.QtCore import QTimer
    QTimer.singleShot(1000, simulate_progress)
    
    sys.exit(app.exec_()) 