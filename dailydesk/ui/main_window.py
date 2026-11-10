"""Main desktop shell: responsive sidebar, keyboard navigation and global styling."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QPainter, QColor, QPixmap, QKeySequence, QShortcut, QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QFrame, QLabel, QPushButton,
    QStackedWidget, QApplication, QScrollArea
)

from dailydesk.core.storage import Store
from dailydesk.ui.theme import stylesheet, colors
from dailydesk.ui.command_palette import CommandPalette
from dailydesk.ui.widgets import label, button
from dailydesk.ui.pages import (
    DashboardPage, TasksPage, NotesPage, PlannerPage, HabitsPage,
    ExpensesPage, FocusPage, SettingsPage,
)

NAVIGATION = [
    ("Dashboard", "◈"), ("Tasks", "✓"), ("Notes", "▤"), ("Planner", "▦"),
    ("Habits", "◉"), ("Expenses", "◫"), ("Focus", "◎"), ("Settings", "⚙"),
]


def icon_pixmap(accent: str) -> QPixmap:
    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(accent))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(5, 5, size - 10, size - 10, 29, 29)
    painter.setPen(QColor("#0B1020"))
    font = QFont("Segoe UI", 49, QFont.Black)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "M")
    painter.end()
    return pixmap


class MainWindow(QMainWindow):
    def __init__(self, store: Store):
        super().__init__()
        self.store = store
        self.theme_name = store.get_pref("theme", "Midnight")
        self.accent_name = store.get_pref("accent", "Violet")
        self.currency = store.get_pref("currency", "PKR")
        self.setWindowTitle("MAH DailyDesk — Your productivity command center")
        self.setMinimumSize(1060, 695)
        self.resize(1320, 810)

        outer = QWidget()
        outer.setObjectName("appRoot")
        self.setCentralWidget(outer)
        root = QHBoxLayout(outer)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(228)
        side = QVBoxLayout(self.sidebar)
        side.setContentsMargins(18, 24, 18, 20)
        side.setSpacing(8)
        brand = QHBoxLayout()
        brand.setSpacing(9)
        mark = QLabel("M")
        mark.setAlignment(Qt.AlignCenter)
        mark.setFixedSize(40, 40)
        mark.setObjectName("logoMark")
        brand.addWidget(mark)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        brand_text.addWidget(label("DailyDesk", "brand"))
        brand_text.addWidget(label("MAH EDITION", "mini"))
        brand.addLayout(brand_text, 1)
        side.addLayout(brand)
        side.addSpacing(29)
        side.addWidget(label("YOUR WORKSPACE", "mini"))
        side.addSpacing(6)
        self.nav_buttons: dict[str, QPushButton] = {}
        for title, glyph in NAVIGATION:
            btn = button(f"{glyph}     {title}", "nav", lambda _=False, t=title: self.navigate(t))
            btn.setProperty("active", "false")
            btn.setMinimumHeight(45)
            btn.setToolTip(f"{title}  •  Ctrl+{len(self.nav_buttons)+1}")
            side.addWidget(btn)
            self.nav_buttons[title] = btn
        side.addStretch()
        foot, fl = self._sidebar_footer()
        side.addWidget(foot)
        root.addWidget(self.sidebar)

        center = QFrame()
        center.setObjectName("center")
        area = QVBoxLayout(center)
        area.setContentsMargins(0, 0, 0, 0)
        area.setSpacing(0)
        self.topbar = QFrame()
        top = QHBoxLayout(self.topbar)
        top.setContentsMargins(29, 15, 29, 13)
        self.breadcrumb = label("Overview", "muted")
        top.addWidget(self.breadcrumb)
        top.addStretch()
        top.addWidget(button("⌕  Search   Ctrl+K", "", self.open_command_palette))
        top.addSpacing(10)
        self.clock = label("", "muted")
        top.addWidget(self.clock)
        top.addSpacing(15)
        self.status_label = label("●  Offline & private", "accent")
        top.addWidget(self.status_label)
        area.addWidget(self.topbar)
        self.stack = QStackedWidget()
        area.addWidget(self.stack, 1)
        root.addWidget(center, 1)
        self.pages = {
            "Dashboard": DashboardPage(store, self), "Tasks": TasksPage(store, self),
            "Notes": NotesPage(store, self), "Planner": PlannerPage(store, self),
            "Habits": HabitsPage(store, self), "Expenses": ExpensesPage(store, self),
            "Focus": FocusPage(store, self), "Settings": SettingsPage(store, self),
        }
        for page in self.pages.values():
            self.stack.addWidget(page)
        self._apply_style()
        self.navigate("Dashboard")
        self._tick_clock()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._tick_clock)
        self.clock_timer.start(30_000)
        self.shortcuts = []
        for i, (name, _) in enumerate(NAVIGATION, 1):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{i}"), self)
            shortcut.activated.connect(lambda n=name: self.navigate(n))
            self.shortcuts.append(shortcut)
        new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_shortcut.activated.connect(lambda: self.navigate("Tasks", new=True))
        self.shortcuts.append(new_shortcut)
        find_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        find_shortcut.activated.connect(self.open_command_palette)
        self.shortcuts.append(find_shortcut)

    def _sidebar_footer(self):
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 15, 12, 15)
        lay.setSpacing(5)
        lay.addWidget(label("✦  YOUR DAILY LEVEL-UP", "accent"))
        lay.addWidget(label("Plan it. Do it. Own it.", "muted"))
        return card, lay

    def _tick_clock(self):
        self.clock.setText(datetime.now().strftime("%a, %d %b  ·  %I:%M %p"))

    def _apply_style(self):
        palette = colors(self.theme_name, self.accent_name)
        app = QApplication.instance()
        app.setStyleSheet(stylesheet(self.theme_name, self.accent_name) +
            "QLabel#logoMark { background: " + palette["accent"] + "; color: " + palette["bg"] +
            "; border-radius: 12px; font-size: 24px; font-weight: 900; }")
        self.setWindowIcon(QIcon(icon_pixmap(palette["accent"])))

    def money(self, cents: int) -> str:
        return f"{self.currency} {cents / 100:,.2f}"

    def navigate(self, title: str, new: bool = False):
        if title not in self.pages:
            return
        page = self.pages[title]
        self.stack.setCurrentWidget(page)
        self.breadcrumb.setText("WORKSPACE   /   " + title.upper())
        for name, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if name == title else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        page.refresh()
        if new:
            if title == "Tasks":
                page.new_task()
            elif title == "Notes":
                page.new_note()

    def open_command_palette(self):
        dialog = CommandPalette(self)
        dialog.exec()

    def apply_preferences(self, theme: str, accent: str, currency: str):
        self.theme_name, self.accent_name, self.currency = theme, accent, currency
        self.store.set_pref("theme", theme)
        self.store.set_pref("accent", accent)
        self.store.set_pref("currency", currency)
        self._apply_style()
        self.pages["Expenses"].refresh()
        self.status("Preferences saved")

    def status(self, message: str):
        self.status_label.setText("●  " + message)
        QTimer.singleShot(3500, lambda: self.status_label.setText("●  Offline & private"))

    def closeEvent(self, event):
        # Save any current note edits before app shutdown.
        self.pages["Notes"]._persist_previous()
        self.store.close()
        event.accept()