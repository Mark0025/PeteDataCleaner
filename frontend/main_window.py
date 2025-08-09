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
    QToolButton, QMessageBox, QDialog, QFrame, QLabel, 
    QPushButton, QScrollArea, QGridLayout, QHBoxLayout
)
from PyQt5.QtGui import QIcon, QFont
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
        self.setWindowTitle('Pete Data Cleaner - Local House Buyers')
        self.resize(1400, 900)
        
        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Application state
        self.current_df = None
        self.current_pete_headers = None
        self.current_mapping = None
        self.rules_config = DEFAULT_RULES_CONFIG.copy()
        
        # Initialize user system
        self._initialize_user_system()
        
        # Menu options configuration
        self.menu_options = {
            'Dashboard': ("Dashboard", True),
            'Upload Data': ("Upload Data", True),
            'Recent Presets': ("Recent Presets", True),
            'Owner Analysis': ("Owner Analysis", True),
            'Export History': ("Export History", True),
            'Settings': ("Settings", True),
            'Exit': ("Exit", True)
        }
        
        # Setup UI
        self._setup_ui()
        
        # Show dashboard on startup
        self.show_dashboard()
    
    def _initialize_user_system(self):
        """Initialize the user system and login default user."""
        try:
            from backend.utils.user_manager import login_default_user, get_dashboard_data
            self.current_user = login_default_user()
            self.dashboard_data = get_dashboard_data()
            logger.info(f"✅ User system initialized: {self.current_user.name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize user system: {e}")
            self.current_user = None
            self.dashboard_data = None
    
    def _setup_ui(self):
        """Setup the main UI components."""
        # Logo
        self.layout.addWidget(create_logo_label())
        
        # User info display
        if self.current_user:
            from PyQt5.QtWidgets import QLabel
            user_info = QLabel(f"👤 {self.current_user.name} | 🏢 {self.current_user.company_id.replace('_', ' ').title()}")
            user_info.setStyleSheet("color: #667eea; font-weight: bold; padding: 5px;")
            self.layout.addWidget(user_info, alignment=Qt.AlignRight)
        
        # Settings buttons
        settings_layout = QHBoxLayout()
        
        # Font settings button
        self.font_settings_btn = QToolButton()
        self.font_settings_btn.setIcon(QIcon.fromTheme('font-x-generic'))
        self.font_settings_btn.setToolTip('Font Settings')
        self.font_settings_btn.clicked.connect(self.open_font_settings)
        settings_layout.addWidget(self.font_settings_btn)
        
        # General settings button
        self.settings_btn = QToolButton()
        self.settings_btn.setIcon(QIcon.fromTheme('preferences-system'))
        self.settings_btn.setToolTip('Settings')
        self.settings_btn.clicked.connect(self.open_settings)
        settings_layout.addWidget(self.settings_btn)
        
        # Add settings layout to the right side
        right_widget = QWidget()
        right_widget.setLayout(settings_layout)
        self.layout.addWidget(right_widget, alignment=Qt.AlignRight)
    
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
    
    def show_dashboard(self):
        """Show the web-app-like dashboard."""
        self.clear_layout()
        
        if not self.dashboard_data:
            self.show_startup_menu()
            return
        
        from PyQt5.QtWidgets import (
            QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
            QLabel, QPushButton, QFrame, QScrollArea
        )
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        # Create dashboard widget
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        
        # Header
        header = QLabel(f"🏠 Welcome back, {self.current_user.name}!")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #667eea; margin: 20px;")
        dashboard_layout.addWidget(header, alignment=Qt.AlignCenter)
        
        # Create scrollable content
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Dashboard grid
        grid_layout = QGridLayout()
        
        # Data Overview Card
        overview_card = self._create_dashboard_card(
            "📊 Data Overview",
            [
                ("Total Presets", f"{self.dashboard_data['presets']['total']}"),
                ("Recent Exports", f"{self.dashboard_data['exports']['total']}"),
                ("Records Exported", f"{self.dashboard_data['exports']['total_records_exported']:,}")
            ]
        )
        grid_layout.addWidget(overview_card, 0, 0)
        
        # Owner Analysis Card
        owner_data = self.dashboard_data['analysis']['owner_analysis']
        owner_card = self._create_dashboard_card(
            "🏠 Owner Analysis",
            [
                ("Total Owners", f"{owner_data.get('total_owners', 0):,}"),
                ("Business Entities", f"{owner_data.get('business_entities', 0):,}"),
                ("Multi-Property Owners", f"{owner_data.get('multi_property_owners', 0):,}")
            ]
        )
        grid_layout.addWidget(owner_card, 0, 1)
        
        # Phone Prioritization Card
        phone_card = self._create_dashboard_card(
            "📞 Phone Prioritization",
            [
                ("Status Weights", "Configured"),
                ("Type Weights", "Configured"),
                ("Tag Weights", "Configured")
            ]
        )
        grid_layout.addWidget(phone_card, 0, 2)
        
        # Quick Actions Card
        actions_card = self._create_quick_actions_card()
        grid_layout.addWidget(actions_card, 1, 0, 1, 3)
        
        # Recent Activity Card
        activity_card = self._create_recent_activity_card()
        grid_layout.addWidget(activity_card, 2, 0, 1, 3)
        
        # Pipeline Status Card (Real-time monitoring)
        pipeline_card = self._create_pipeline_status_card()
        grid_layout.addWidget(pipeline_card, 3, 0, 1, 3)
        
        scroll_layout.addLayout(grid_layout)
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        
        dashboard_layout.addWidget(scroll_area)
        self.layout.addWidget(dashboard_widget)
    
    def _create_dashboard_card(self, title: str, metrics: list) -> QFrame:
        """Create a dashboard card with metrics."""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
        from PyQt5.QtGui import QFont
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #333; border-bottom: 2px solid #667eea; padding-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Metrics
        for metric_name, metric_value in metrics:
            metric_layout = QHBoxLayout()
            
            name_label = QLabel(metric_name)
            name_label.setStyleSheet("color: #666;")
            
            value_label = QLabel(str(metric_value))
            value_label.setStyleSheet("color: #667eea; font-weight: bold;")
            
            metric_layout.addWidget(name_label)
            metric_layout.addStretch()
            metric_layout.addWidget(value_label)
            
            layout.addLayout(metric_layout)
        
        return card
    
    def _create_quick_actions_card(self) -> QFrame:
        """Create quick actions card."""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QPushButton
        from PyQt5.QtGui import QFont
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title_label = QLabel("⚡ Quick Actions")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #333; border-bottom: 2px solid #667eea; padding-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Actions grid
        actions_layout = QGridLayout()
        
        actions = [
            ("📁 Upload New Data", self.show_file_selector),
            ("🔄 Load Recent Preset", self.show_recent_presets),
            ("🏠 View Owner Analysis", self.show_owner_analysis),
            ("📊 Export History", self.show_export_history)
        ]
        
        for i, (text, callback) in enumerate(actions):
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #667eea;
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #5a6fd8;
                }
            """)
            btn.clicked.connect(callback)
            actions_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(actions_layout)
        return card
    
    def _create_recent_activity_card(self) -> QFrame:
        """Create recent activity card."""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
        from PyQt5.QtGui import QFont
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Title
        title_label = QLabel("📋 Recent Activity")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setStyleSheet("color: #333; border-bottom: 2px solid #667eea; padding-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Latest preset
        if self.dashboard_data['presets']['recent']:
            latest_preset = self.dashboard_data['presets']['recent'][0]
            preset_text = f"Latest Preset: {latest_preset['preset_name']} ({latest_preset['created_at'][:10]})"
        else:
            preset_text = "Latest Preset: No presets yet"
        
        preset_label = QLabel(preset_text)
        preset_label.setStyleSheet("color: #667eea; font-weight: bold;")
        layout.addWidget(preset_label)
        
        # Latest export
        if self.dashboard_data['exports']['recent']:
            latest_export = self.dashboard_data['exports']['recent'][-1]
            export_text = f"Latest Export: {latest_export.get('export_records', 0):,} records ({latest_export.get('timestamp', '')[:10]})"
        else:
            export_text = "Latest Export: No exports yet"
        
        export_label = QLabel(export_text)
        export_label.setStyleSheet("color: #667eea; font-weight: bold;")
        layout.addWidget(export_label)
        
        return card
    
    def show_recent_presets(self):
        """Show recent presets interface."""
        self.clear_layout()
        
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QFrame, QScrollArea
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        # Create presets widget
        presets_widget = QWidget()
        presets_layout = QVBoxLayout(presets_widget)
        
        # Header
        header = QLabel("🔄 Recent Presets")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #667eea; margin: 20px;")
        presets_layout.addWidget(header, alignment=Qt.AlignCenter)
        
        # Create scrollable content
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        if self.dashboard_data and self.dashboard_data['presets']['recent']:
            for preset in self.dashboard_data['presets']['recent']:
                preset_card = self._create_preset_card(preset)
                scroll_layout.addWidget(preset_card)
        else:
            no_presets = QLabel("No presets found. Upload data to create your first preset!")
            no_presets.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
            scroll_layout.addWidget(no_presets)
        
        # Back button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd8;
            }
        """)
        back_btn.clicked.connect(self.show_dashboard)
        scroll_layout.addWidget(back_btn)
        
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        presets_layout.addWidget(scroll_area)
        
        self.layout.addWidget(presets_widget)
    
    def _create_preset_card(self, preset: dict) -> QFrame:
        """Create a preset card."""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PyQt5.QtGui import QFont
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Preset info
        name_label = QLabel(preset['preset_name'])
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet("color: #333;")
        layout.addWidget(name_label)
        
        date_label = QLabel(f"Created: {preset['created_at'][:10]}")
        date_label.setStyleSheet("color: #666;")
        layout.addWidget(date_label)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        load_btn = QPushButton("Load Preset")
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        load_btn.clicked.connect(lambda: self._load_preset(preset['preset_id']))
        
        view_btn = QPushButton("View Details")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        view_btn.clicked.connect(lambda: self._view_preset_details(preset['preset_id']))
        
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(view_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        return card
    
    def show_owner_analysis(self):
        """Show owner analysis interface."""
        self.clear_layout()
        
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        # Create owner analysis widget
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # Header
        header = QLabel("🏠 Owner Analysis")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #667eea; margin: 20px;")
        analysis_layout.addWidget(header, alignment=Qt.AlignCenter)
        
        # Analysis content
        if self.dashboard_data and self.dashboard_data['analysis']['owner_analysis']:
            owner_data = self.dashboard_data['analysis']['owner_analysis']
            
            # Create analysis cards
            analysis_card = self._create_dashboard_card(
                "📊 Analysis Summary",
                [
                    ("Total Owners", f"{owner_data.get('total_owners', 0):,}"),
                    ("Business Entities", f"{owner_data.get('business_entities', 0):,}"),
                    ("Multi-Property Owners", f"{owner_data.get('multi_property_owners', 0):,}")
                ]
            )
            analysis_layout.addWidget(analysis_card)
        else:
            no_data = QLabel("No owner analysis data available. Upload data and run analysis first.")
            no_data.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
            analysis_layout.addWidget(no_data)
        
        # Back button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd8;
            }
        """)
        back_btn.clicked.connect(self.show_dashboard)
        analysis_layout.addWidget(back_btn)
        
        self.layout.addWidget(analysis_widget)
    
    def show_export_history(self):
        """Show export history interface."""
        self.clear_layout()
        
        from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        # Create export history widget
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        
        # Header
        header = QLabel("📊 Export History")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setStyleSheet("color: #667eea; margin: 20px;")
        history_layout.addWidget(header, alignment=Qt.AlignCenter)
        
        # Export history content
        if self.dashboard_data and self.dashboard_data['exports']['recent']:
            for export in self.dashboard_data['exports']['recent']:
                export_card = self._create_export_card(export)
                history_layout.addWidget(export_card)
        else:
            no_exports = QLabel("No export history available.")
            no_exports.setStyleSheet("color: #666; font-style: italic; padding: 20px;")
            history_layout.addWidget(no_exports)
        
        # Back button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd8;
            }
        """)
        back_btn.clicked.connect(self.show_dashboard)
        history_layout.addWidget(back_btn)
        
        self.layout.addWidget(history_widget)
    
    def _create_export_card(self, export: dict) -> QFrame:
        """Create an export card."""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
        from PyQt5.QtGui import QFont
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Export info
        records_label = QLabel(f"Records: {export.get('export_records', 0):,}")
        records_label.setFont(QFont("Arial", 14, QFont.Bold))
        records_label.setStyleSheet("color: #333;")
        layout.addWidget(records_label)
        
        date_label = QLabel(f"Date: {export.get('timestamp', '')[:10]}")
        date_label.setStyleSheet("color: #666;")
        layout.addWidget(date_label)
        
        return card
    
    def _load_preset(self, preset_id: str):
        """Load a preset."""
        # TODO: Implement preset loading
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Preset Loading", f"Loading preset: {preset_id}")
    
    def _view_preset_details(self, preset_id: str):
        """View preset details."""
        # TODO: Implement preset details view
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Preset Details", f"Viewing details for: {preset_id}")
    
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
        if name == "Dashboard":
            self.show_dashboard()
        elif name == "Upload Data":
            self.show_file_selector()
        elif name == "Recent Presets":
            self.show_recent_presets()
        elif name == "Owner Analysis":
            self.show_owner_analysis()
        elif name == "Export History":
            self.show_export_history()
        elif name == "Settings":
            self.open_settings()
        elif name == "Exit":
            self.close()
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
    
    def open_font_settings(self):
        """Open font settings dialog."""
        from frontend.dialogs.font_settings_dialog import show_font_settings_dialog
        settings = show_font_settings_dialog(self)
        if settings:
            self.apply_font_settings(settings)
    
    def apply_font_settings(self, settings: dict):
        """Apply font settings to the application."""
        from PyQt5.QtGui import QFont
        from PyQt5.QtWidgets import QApplication
        
        # Create font from settings
        font = QFont()
        font.setFamily(settings.get("font_family", "Arial"))
        font.setPointSize(settings.get("font_size", 12))
        
        # Set font weight
        weight_text = settings.get("font_weight", "Normal (400)")
        if "Light" in weight_text:
            font.setWeight(QFont.Light)
        elif "Bold" in weight_text:
            font.setWeight(QFont.Bold)
        elif "Extra Bold" in weight_text:
            font.setWeight(QFont.ExtraBold)
        else:
            font.setWeight(QFont.Normal)
        
        # Set additional options
        if settings.get("antialiasing", True):
            font.setStyleStrategy(QFont.PreferAntialias)
        
        # Apply to application
        QApplication.setFont(font)
        
        # Update status
        print(f"✅ Applied font: {settings.get('font_family')} {settings.get('font_size')}pt")
    
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

    def _create_pipeline_status_card(self) -> QFrame:
        """Create a pipeline status monitoring card."""
        from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
        from PyQt5.QtGui import QFont
        from PyQt5.QtCore import QTimer, Qt
        import os
        import time
        
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #667eea;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Header
        header = QLabel("🚀 Pipeline Status Monitor")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #667eea; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Status indicators
        status_layout = QHBoxLayout()
        
        # Current step
        self.current_step_label = QLabel("⏳ Waiting for pipeline...")
        self.current_step_label.setStyleSheet("color: #666; font-weight: bold;")
        status_layout.addWidget(self.current_step_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #667eea;
                border-radius: 3px;
            }
        """)
        status_layout.addWidget(self.progress_bar)
        
        layout.addLayout(status_layout)
        
        # Details
        self.pipeline_details = QLabel("No active pipeline detected")
        self.pipeline_details.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.pipeline_details)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Status")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6fd8;
            }
        """)
        refresh_btn.clicked.connect(self._refresh_pipeline_status)
        button_layout.addWidget(refresh_btn)
        
        view_logs_btn = QPushButton("📋 View Logs")
        view_logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        view_logs_btn.clicked.connect(self._view_pipeline_logs)
        button_layout.addWidget(view_logs_btn)
        
        layout.addLayout(button_layout)
        
        # Set up auto-refresh timer
        self.pipeline_timer = QTimer()
        self.pipeline_timer.timeout.connect(self._refresh_pipeline_status)
        self.pipeline_timer.start(5000)  # Refresh every 5 seconds
        
        return card
    
    def _refresh_pipeline_status(self):
        """Refresh the pipeline status display."""
        try:
            # Check for recent pipeline activity
            import glob
            import time
            from pathlib import Path
            
            # Look for recent export files
            export_files = glob.glob("data/exports/pete_export_*.csv") + glob.glob("data/exports/pete_export_*.xlsx")
            owner_files = glob.glob("data/exports/owner_objects_summary_*.csv") + glob.glob("data/exports/owner_objects_summary_*.xlsx")
            
            # Check for recent data files
            data_files = glob.glob("data/processed/enhanced_data/*/enhanced_data.csv")
            
            if export_files or owner_files:
                # Pipeline completed recently
                self.current_step_label.setText("✅ Pipeline Completed!")
                self.current_step_label.setStyleSheet("color: #28a745; font-weight: bold;")
                self.progress_bar.setValue(100)
                
                latest_export = max(export_files, key=os.path.getctime) if export_files else "None"
                latest_owner = max(owner_files, key=os.path.getctime) if owner_files else "None"
                
                # Calculate completion time
                completion_time = os.path.getctime(latest_export if export_files else latest_owner)
                time_since_completion = time.time() - completion_time
                
                self.pipeline_details.setText(
                    f"Latest export: {os.path.basename(latest_export) if export_files else 'None'}\n"
                    f"Latest owner analysis: {os.path.basename(latest_owner) if owner_files else 'None'}\n"
                    f"Completed {int(time_since_completion)}s ago"
                )
                
            elif data_files:
                # Pipeline in progress
                latest_data = max(data_files, key=os.path.getctime)
                file_time = os.path.getctime(latest_data)
                time_diff = time.time() - file_time
                
                if time_diff < 300:  # Within 5 minutes
                    self.current_step_label.setText("🔄 Pipeline Running...")
                    self.current_step_label.setStyleSheet("color: #ffc107; font-weight: bold;")
                    
                    # Estimate progress and time remaining
                    progress, eta = self._estimate_pipeline_progress(time_diff)
                    self.progress_bar.setValue(progress)
                    
                    # Format ETA nicely
                    if eta > 60:
                        eta_text = f"{int(eta/60)}m {int(eta%60)}s remaining"
                    else:
                        eta_text = f"{int(eta)}s remaining"
                    
                    self.pipeline_details.setText(
                        f"Processing data... (Last update: {int(time_diff)}s ago)\n"
                        f"⏱️ Estimated: {eta_text}\n"
                        f"📊 Progress: {progress}%"
                    )
                else:
                    self.current_step_label.setText("⏸️ Pipeline Paused")
                    self.current_step_label.setStyleSheet("color: #ffc107; font-weight: bold;")
                    self.progress_bar.setValue(50)
                    self.pipeline_details.setText("Pipeline may be paused or completed")
                    
            else:
                # No recent activity
                self.current_step_label.setText("⏳ No Active Pipeline")
                self.current_step_label.setStyleSheet("color: #666; font-weight: bold;")
                self.progress_bar.setValue(0)
                self.pipeline_details.setText("Ready to start pipeline")
                
        except Exception as e:
            self.pipeline_details.setText(f"Error checking status: {str(e)}")
    
    def _estimate_pipeline_progress(self, time_since_last_update: float) -> tuple[int, float]:
        """
        Estimate pipeline progress and time remaining based on typical timings.
        
        Args:
            time_since_last_update: Seconds since last file update
            
        Returns:
            tuple: (progress_percentage, estimated_seconds_remaining)
        """
        # Typical pipeline timings for 310K rows (based on our speed tests)
        typical_timings = {
            'load': 5,      # 5 seconds
            'clean': 10,    # 10 seconds  
            'filter': 5,    # 5 seconds
            'phones': 15,   # 15 seconds
            'owners': 30,   # 30 seconds
            'mapping': 10,  # 10 seconds
            'standardize': 5, # 5 seconds
            'export_csv': 2,  # 2 seconds
            'export_excel': 52, # 52 seconds (xlsxwriter) - 310K rows / 6000 rows/sec
            'owner_excel': 34   # 34 seconds (xlsxwriter) - 270K rows / 8000 rows/sec
        }
        
        total_expected_time = sum(typical_timings.values())
        
        # If we're in the export phase (after CSV is done), estimate based on Excel export
        if time_since_last_update > 80:  # Likely in Excel export phase
            # Assume we're in Excel export (52s) or owner Excel export (34s)
            if time_since_last_update < 132:  # Still in main Excel export
                progress = 85 + (time_since_last_update - 80) / 52 * 10  # 85-95%
                eta = max(0, 52 - (time_since_last_update - 80))
            else:  # In owner Excel export
                progress = 95 + (time_since_last_update - 132) / 34 * 5  # 95-100%
                eta = max(0, 34 - (time_since_last_update - 132))
        else:
            # Estimate based on typical progress
            progress = min(85, (time_since_last_update / total_expected_time) * 85)
            eta = max(0, total_expected_time - time_since_last_update)
        
        return int(progress), eta
    
    def _view_pipeline_logs(self):
        """View pipeline logs."""
        try:
            import subprocess
            import sys
            
            # Try to open the most recent log file
            log_files = [
                "backend.log",
                "data/processed/enhanced_data/*/metadata.json",
                "data/processed/owner_objects/*/summary.json"
            ]
            
            for pattern in log_files:
                import glob
                files = glob.glob(pattern)
                if files:
                    latest_file = max(files, key=os.path.getctime)
                    if sys.platform == "darwin":  # macOS
                        subprocess.run(["open", latest_file])
                    elif sys.platform == "win32":  # Windows
                        subprocess.run(["notepad", latest_file])
                    else:  # Linux
                        subprocess.run(["xdg-open", latest_file])
                    return
            
            # If no log files found, show a message
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "Pipeline Logs", 
                "No recent log files found. Check the console output for pipeline status."
            )
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Error", 
                f"Could not open logs: {str(e)}"
            )

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