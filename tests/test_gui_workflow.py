"""GUI workflow integration tests (headless).

Uses pytest-qt's *qtbot* fixture for stable widget handling.
Only lightweight sanity checks are performed to keep CI fast.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from PyQt5.QtWidgets import QApplication
from pytestqt.qtbot import QtBot
from PyQt5.QtCore import Qt

# Ensure project root on path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from frontend.main_window import MainWindow  # noqa: E402


@pytest.fixture(scope="session")
def app() -> QApplication:  # noqa: D401
    """Provide a QApplication instance for the entire test session."""
    return QApplication.instance() or QApplication([])


@pytest.fixture()
def main_window(app: QApplication, qtbot: QtBot) -> MainWindow:  # noqa: D401
    """Create and show the MainWindow widget."""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    return window


def test_startup_menu_visible(main_window: MainWindow) -> None:
    """The startup menu should be present after launch."""
    assert hasattr(main_window, "menu")
    assert main_window.menu is not None


def test_strip_dot_button_insertion(qtbot: QtBot, main_window: MainWindow, tmp_path: Path) -> None:
    """Verify the 'Strip .0' button cleans data in Data Tools panel."""
    # Simulate selecting GUI Mapping Tool from the startup menu
    main_window.handle_menu_select("GUI Mapping Tool")

    # Ensure file selector exists
    file_selector = main_window.file_selector
    assert file_selector is not None

    # Create a sample CSV for upload
    df = pd.DataFrame({"Phone 1": [123.0, 456.0], "Name": ["A", "B"]})
    sample_path = tmp_path / "sample.csv"
    df.to_csv(sample_path, index=False)

    # Make the upload dir & copy file so selector can find it
    upload_dir = ROOT_DIR / "upload"
    upload_dir.mkdir(exist_ok=True)
    sample_dest = upload_dir / sample_path.name
    sample_dest.write_bytes(sample_path.read_bytes())

    # Refresh list and select file
    file_selector.refresh_file_list()
    file_selector.file_combo.setCurrentText(sample_path.name)

    # Preview table to load dataframe
    file_selector.preview_table()
    assert hasattr(file_selector, "df") and not file_selector.df.empty

    # Click "Strip .0" button
    tools_panel = main_window.data_tools_panel  # type: ignore[attr-defined]
    strip_button = None
    from PyQt5.QtWidgets import QPushButton  # type: ignore
    
    # Locate the button within the tools panel
    for button in tools_panel.findChildren(QPushButton):
        if "Strip .0" in button.text():
            strip_button = button
            break
    assert strip_button is not None, "Strip .0 button not found"

    qtbot.mouseClick(strip_button, Qt.LeftButton)  # type: ignore[name-defined]

    # Data should now be cleaned (no trailing .0)
    cleaned_df = tools_panel.data_prep_editor.get_prepared_data()  # type: ignore[attr-defined]
    assert cleaned_df is not None
    assert cleaned_df["Phone 1"].tolist() == ["123", "456"]
