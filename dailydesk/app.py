"""Application launcher shared by direct, module and pip-installed entry points."""
from __future__ import annotations

import sys
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox

from dailydesk.core.storage import Store
from dailydesk.ui.main_window import MainWindow


def launch() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("MAH DailyDesk")
    app.setOrganizationName("MAH")
    app.setFont(QFont("Segoe UI", 10))
    try:
        store = Store()
    except Exception as exc:
        QMessageBox.critical(None, "MAH DailyDesk", f"Unable to open local database:\n{exc}")
        return 1
    window = MainWindow(store)
    window.show()
    return app.exec()