"""Keyboard-first command palette for global navigation and quick search."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel,
)


class CommandPalette(QDialog):
    def __init__(self, main):
        super().__init__(main)
        self.main = main
        self.setWindowTitle("Quick launch & search")
        self.setMinimumSize(540, 440)
        self.setMaximumHeight(540)
        self.setModal(True)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 22, 22, 22)
        lay.setSpacing(11)
        title = QLabel("✦  Quick launch")
        title.setObjectName("sectionTitle")
        lay.addWidget(title)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search sections, tasks, notes, activities...")
        self.search.textChanged.connect(self.populate)
        self.search.returnPressed.connect(self.launch)
        lay.addWidget(self.search)
        self.results = QListWidget()
        self.results.itemDoubleClicked.connect(lambda *_: self.launch())
        lay.addWidget(self.results, 1)
        help_label = QLabel("↑ ↓ Navigate    ·    Enter Open    ·    Esc Close")
        help_label.setObjectName("mini")
        lay.addWidget(help_label)
        self.populate()

    def populate(self):
        query = self.search.text().strip()
        self.results.clear()
        found = []
        for name in self.main.pages:
            if not query or query.lower() in name.lower():
                found.append((f"↗   Open {name}", name, ""))
        if query:
            for row in self.main.store.tasks(query)[:8]:
                found.append((f'✓   Task  ·  {row["title"]}', "Tasks", query))
            for row in self.main.store.notes(query)[:8]:
                found.append((f'▤   Note  ·  {row["title"]}', "Notes", query))
            for row in self.main.store.plans(query)[:8]:
                found.append((f'▦   Plan  ·  {row["title"]}', "Planner", query))
        for title, page, phrase in found[:26]:
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, (page, phrase))
            self.results.addItem(item)
        if self.results.count():
            self.results.setCurrentRow(0)

    def launch(self):
        selected = self.results.currentItem()
        if selected is None:
            return
        page, query = selected.data(Qt.UserRole)
        self.accept()
        self.main.navigate(page)
        if query:
            search_field = getattr(self.main.pages[page], "search", None)
            if search_field is not None:
                search_field.setText(query)
                search_field.setFocus()