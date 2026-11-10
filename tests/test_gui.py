"""Open the actual Qt app offscreen to catch widget-construction errors."""
from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

PySide6 = pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from dailydesk.core.storage import Store
from dailydesk.ui.main_window import MainWindow


def test_window_boot_and_navigation(tmp_path):
    app = QApplication.instance() or QApplication([])
    store = Store(tmp_path / "gui.sqlite3")
    window = MainWindow(store)
    assert window.stack.count() == 8
    for name in window.pages:
        window.navigate(name)
        assert window.stack.currentWidget() is window.pages[name]
    window.apply_preferences("Daylight", "Cyan", "USD")
    assert store.get_pref("theme") == "Daylight"
    assert store.get_pref("currency") == "USD"
    window.close()