import os

# Paths
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'upload')
LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'public', 'pete.png')

# Default Configuration
DEFAULT_RULES_CONFIG = {
    'fuzzy_threshold': 80,
    'preview_row_count': 10,
    'preview_col_count': 10,
    'show_not_mapped_in_report': True,
    'disable_fuzzy': False,
    'empty_column_config': {
        'filter_empty_columns': True,
        'empty_column_threshold': 0.9
    }
}

# CLI Options
CLI_OPTIONS = [
    ("Workspace", "Manage Google Sheets workspace (list, search, add, select, browse)"),
    ("Standardize", "Standardize uploaded data files to Pete template"),
    ("Rules", "Rule management utilities (coming soon)"),
    ("Backend", "Backend/analysis utilities (coming soon)"),
    ("Test", "Run all tests and show what's working"),
    ("GUI Mapping Tool", "Launch the GUI mapping tool for visual column mapping"),
    ("Exit", "Exit the application")
]

# Default Sheet Configuration
DEFAULT_SHEET_CONFIG = {
    'sheet_id': '11M1wYpVdfQfZOM3y5GSVj75FuYCQ0qVtOt4MbUpbZzw',
    'tab_name': 'Sheet1'
} 