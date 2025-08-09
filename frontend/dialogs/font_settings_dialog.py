#!/usr/bin/env python3
"""
Font Settings Dialog

Provides font configuration options for the application.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QSpinBox, QCheckBox, QPushButton,
    QLabel, QGroupBox, QTextEdit, QSlider
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase
from typing import Dict, Any, Optional
import json
from pathlib import Path
from loguru import logger


class FontSettingsDialog(QDialog):
    """
    Font configuration dialog.
    
    Features:
    - Font family selection
    - Font size controls
    - Font weight options
    - Live preview
    - Settings persistence
    """
    
    # Signal emitted when font settings change
    font_settings_changed = pyqtSignal(dict)  # new_settings
    
    def __init__(self, parent=None):
        """Initialize font settings dialog."""
        super().__init__(parent)
        
        self.settings_file = Path("data/users/preferences/font_settings.json")
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.current_settings = self._load_settings()
        self._setup_ui()
        self._apply_current_settings()
    
    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Font Settings")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Font Family Section
        family_group = QGroupBox("Font Family")
        family_layout = QFormLayout(family_group)
        
        self.family_combo = QComboBox()
        self._populate_font_families()
        self.family_combo.currentTextChanged.connect(self._update_preview)
        family_layout.addRow("Font Family:", self.family_combo)
        
        layout.addWidget(family_group)
        
        # Font Size Section
        size_group = QGroupBox("Font Size")
        size_layout = QFormLayout(size_group)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setSuffix(" pt")
        self.size_spin.valueChanged.connect(self._update_preview)
        size_layout.addRow("Font Size:", self.size_spin)
        
        # Size slider for quick adjustment
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(8, 72)
        self.size_slider.valueChanged.connect(self.size_spin.setValue)
        self.size_spin.valueChanged.connect(self.size_slider.setValue)
        size_layout.addRow("Quick Adjust:", self.size_slider)
        
        layout.addWidget(size_group)
        
        # Font Weight Section
        weight_group = QGroupBox("Font Weight")
        weight_layout = QFormLayout(weight_group)
        
        self.weight_combo = QComboBox()
        self.weight_combo.addItems([
            "Normal (400)",
            "Light (300)", 
            "Bold (700)",
            "Extra Bold (800)"
        ])
        self.weight_combo.currentTextChanged.connect(self._update_preview)
        weight_layout.addRow("Font Weight:", self.weight_combo)
        
        layout.addWidget(weight_group)
        
        # Additional Options
        options_group = QGroupBox("Additional Options")
        options_layout = QFormLayout(options_group)
        
        self.antialiasing_check = QCheckBox("Enable Antialiasing")
        self.antialiasing_check.setChecked(True)
        self.antialiasing_check.toggled.connect(self._update_preview)
        options_layout.addRow(self.antialiasing_check)
        
        self.kerning_check = QCheckBox("Enable Kerning")
        self.kerning_check.setChecked(True)
        self.kerning_check.toggled.connect(self._update_preview)
        options_layout.addRow(self.kerning_check)
        
        layout.addWidget(options_group)
        
        # Preview Section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setPlainText(
            "This is a preview of how your font settings will look.\n"
            "The quick brown fox jumps over the lazy dog.\n"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ\n"
            "abcdefghijklmnopqrstuvwxyz\n"
            "0123456789"
        )
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_settings)
        self.apply_btn.setDefault(True)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_font_families(self):
        """Populate font family combo box with available fonts."""
        font_db = QFontDatabase()
        families = font_db.families()
        
        # Sort and filter for common fonts first
        common_fonts = [
            "Arial", "Helvetica", "Times New Roman", "Times",
            "Courier New", "Courier", "Verdana", "Georgia",
            "Tahoma", "Trebuchet MS", "Comic Sans MS", "Impact"
        ]
        
        # Add common fonts first
        for font in common_fonts:
            if font in families:
                self.family_combo.addItem(font)
        
        # Add separator if we have common fonts
        if self.family_combo.count() > 0:
            self.family_combo.insertSeparator(self.family_combo.count())
        
        # Add all other fonts
        for font in sorted(families):
            if font not in common_fonts:
                self.family_combo.addItem(font)
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load font settings from file."""
        default_settings = {
            "font_family": "Arial",
            "font_size": 12,
            "font_weight": "Normal (400)",
            "antialiasing": True,
            "kerning": True
        }
        
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except Exception as e:
                logger.error(f"Failed to load font settings: {e}")
        
        return default_settings
    
    def _save_settings(self, settings: Dict[str, Any]):
        """Save font settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            logger.info("Font settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save font settings: {e}")
    
    def _apply_current_settings(self):
        """Apply current settings to UI controls."""
        settings = self.current_settings
        
        # Set font family
        index = self.family_combo.findText(settings.get("font_family", "Arial"))
        if index >= 0:
            self.family_combo.setCurrentIndex(index)
        
        # Set font size
        self.size_spin.setValue(settings.get("font_size", 12))
        
        # Set font weight
        index = self.weight_combo.findText(settings.get("font_weight", "Normal (400)"))
        if index >= 0:
            self.weight_combo.setCurrentIndex(index)
        
        # Set additional options
        self.antialiasing_check.setChecked(settings.get("antialiasing", True))
        self.kerning_check.setChecked(settings.get("kerning", True))
        
        # Update preview
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview text with current font settings."""
        font = self._get_current_font()
        self.preview_text.setFont(font)
    
    def _get_current_font(self) -> QFont:
        """Get QFont object from current settings."""
        font = QFont()
        
        # Set font family
        font.setFamily(self.family_combo.currentText())
        
        # Set font size
        font.setPointSize(self.size_spin.value())
        
        # Set font weight
        weight_text = self.weight_combo.currentText()
        if "Light" in weight_text:
            font.setWeight(QFont.Light)
        elif "Bold" in weight_text:
            font.setWeight(QFont.Bold)
        elif "Extra Bold" in weight_text:
            font.setWeight(QFont.ExtraBold)
        else:
            font.setWeight(QFont.Normal)
        
        # Set additional options
        font.setStyleStrategy(
            QFont.PreferAntialias if self.antialiasing_check.isChecked() 
            else QFont.PreferDefault
        )
        
        return font
    
    def _get_current_settings(self) -> Dict[str, Any]:
        """Get current settings from UI controls."""
        return {
            "font_family": self.family_combo.currentText(),
            "font_size": self.size_spin.value(),
            "font_weight": self.weight_combo.currentText(),
            "antialiasing": self.antialiasing_check.isChecked(),
            "kerning": self.kerning_check.isChecked()
        }
    
    def _reset_to_defaults(self):
        """Reset settings to defaults."""
        self.current_settings = {
            "font_family": "Arial",
            "font_size": 12,
            "font_weight": "Normal (400)",
            "antialiasing": True,
            "kerning": True
        }
        self._apply_current_settings()
    
    def _apply_settings(self):
        """Apply current settings and close dialog."""
        new_settings = self._get_current_settings()
        
        # Save settings
        self._save_settings(new_settings)
        
        # Emit signal
        self.font_settings_changed.emit(new_settings)
        
        # Close dialog
        self.accept()
    
    def get_font_settings(self) -> Dict[str, Any]:
        """Get current font settings."""
        return self._get_current_settings()
    
    @staticmethod
    def get_application_font() -> QFont:
        """Get the application font from saved settings."""
        settings_file = Path("data/users/preferences/font_settings.json")
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    
                font = QFont()
                font.setFamily(settings.get("font_family", "Arial"))
                font.setPointSize(settings.get("font_size", 12))
                
                weight_text = settings.get("font_weight", "Normal (400)")
                if "Light" in weight_text:
                    font.setWeight(QFont.Light)
                elif "Bold" in weight_text:
                    font.setWeight(QFont.Bold)
                elif "Extra Bold" in weight_text:
                    font.setWeight(QFont.ExtraBold)
                else:
                    font.setWeight(QFont.Normal)
                
                if settings.get("antialiasing", True):
                    font.setStyleStrategy(QFont.PreferAntialias)
                
                return font
            except Exception as e:
                logger.error(f"Failed to load application font: {e}")
        
        # Return default font
        return QFont("Arial", 12)


# Convenience function for easy integration
def show_font_settings_dialog(parent=None) -> Optional[Dict[str, Any]]:
    """Show font settings dialog and return settings if applied."""
    dialog = FontSettingsDialog(parent)
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_font_settings()
    return None


if __name__ == "__main__":
    # Test the font settings dialog
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Show font settings dialog
    settings = show_font_settings_dialog()
    if settings:
        print("Applied font settings:", settings)
    
    sys.exit(app.exec_()) 