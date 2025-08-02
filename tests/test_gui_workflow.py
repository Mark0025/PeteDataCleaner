import os
import sys
import unittest
import pandas as pd
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from frontend.main_window import MainWindow
from backend.utils.data_standardizer import DataStandardizer

class TestGUIMappingWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the application for testing"""
        cls.app = QApplication(sys.argv)
        cls.window = MainWindow()

    def test_startup_menu_exists(self):
        """Verify startup menu is displayed"""
        self.assertTrue(hasattr(self.window, 'menu'))
        self.assertIsNotNone(self.window.menu)

    def test_file_selector_navigation(self):
        """Test navigation to file selector"""
        # Simulate selecting GUI Mapping Tool
        self.window.handle_menu_select("GUI Mapping Tool")
        
        # Verify file selector is displayed
        self.assertTrue(hasattr(self.window, 'file_selector'))
        self.assertIsNotNone(self.window.file_selector)

    def test_file_upload_and_preview(self):
        """Test file upload and preview functionality"""
        # Create a sample CSV for testing
        sample_data = {
            'First Name': ['John', 'Jane', 'Alice'],
            'Last Name': ['Doe', 'Smith', 'Johnson'],
            'Address': ['123 Main St', '456 Elm St', '789 Oak St']
        }
        sample_df = pd.DataFrame(sample_data)
        
        # Save sample data to upload directory
        upload_dir = os.path.join(project_root, 'upload')
        os.makedirs(upload_dir, exist_ok=True)
        sample_path = os.path.join(upload_dir, 'test_sample.csv')
        sample_df.to_csv(sample_path, index=False)

        # Refresh file list and select the test file
        self.window.file_selector.refresh_file_list()
        
        # Simulate selecting the test file
        self.window.file_selector.file_combo.setCurrentText('test_sample.csv')
        
        # Preview the table
        self.window.file_selector.preview_table()
        
        # Verify preview was successful
        self.assertTrue(hasattr(self.window.file_selector, 'df'))
        self.assertFalse(self.window.file_selector.df.empty)

    def test_mapping_workflow(self):
        """Test complete mapping workflow"""
        # Simulate file selection and preview
        self.test_file_upload_and_preview()
        
        # Simulate mapping to Pete headers
        self.window.file_selector.map_to_pete_headers()
        
        # Verify mapping UI is displayed
        self.assertTrue(hasattr(self.window, 'mapping_ui'))
        self.assertIsNotNone(self.window.mapping_ui)

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        # Close the application
        cls.window.close()
        cls.app.quit()

if __name__ == '__main__':
    unittest.main() 