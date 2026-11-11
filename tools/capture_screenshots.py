"""Capture authentic Qt screens with disposable demo data, not private user data."""
from __future__ import annotations

import os
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from dailydesk.core.storage import Store
from dailydesk.ui.main_window import MainWindow


def main() -> None:
    out = Path("screenshots")
    out.mkdir(exist_ok=True)
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory(prefix="dailydesk-demo-") as folder:
        store = Store(Path(folder) / "demo.sqlite3")
        today = date.today()
        store.save_task("Review project milestones", "Organize the coming week", "High", "Projects", today.isoformat())
        store.save_task("Prepare tomorrow's agenda", "", "Medium", "Personal", (today + timedelta(days=1)).isoformat())
        store.save_task("Finish a focused study session", "", "Low", "Learning", status="Done")
        store.save_note("Welcome to DailyDesk", "A private, offline home for your plans, tasks and ideas.", "welcome, demo")
        store.add_habit("Read for 20 minutes")
        store.add_habit("Plan my day")
        store.add_expense("Stationery and notebook", 125000, "Education", today.isoformat())
        store.save_plan("Deep work", datetime.now().replace(hour=14, minute=0).isoformat(timespec="minutes"), 50)
        window = MainWindow(store)
        window.show()
        for name, filename in (("Dashboard", "dashboard.png"), ("Tasks", "tasks.png"), ("Settings", "settings.png")):
            window.navigate(name)
            for _ in range(10):
                app.processEvents()
            image = window.grab()
            if image.isNull() or image.width() < 800:
                raise RuntimeError(f"Could not capture {name} window")
            if not image.save(str(out / filename)):
                raise RuntimeError(f"Failed to save screenshot: {filename}")
            print(f"Saved {out / filename}: {image.width()}x{image.height()}")
        window.close()


if __name__ == "__main__":
    main()