"""Functional productivity pages for the desktop UI."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from PySide6.QtCore import Qt, QDate, QDateTime, QTimer, QUrl, QSignalBlocker
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QPushButton,
    QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QDialog, QDialogButtonBox, QMessageBox,
    QFormLayout, QCheckBox, QDateEdit, QDateTimeEdit, QSpinBox, QDoubleSpinBox,
    QProgressBar, QCalendarWidget, QFileDialog, QScrollArea, QSplitter,
    QSizePolicy, QAbstractItemView
)

from dailydesk.core.storage import Store, data_directory
from dailydesk.ui.theme import colors
from dailydesk.ui.widgets import label, button, card, section_header, style_table, MetricCard, BarChart, clear_layout


class Page(QWidget):
    def __init__(self, store: Store, main):
        super().__init__()
        self.store = store
        self.main = main
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setContentsMargins(28, 25, 28, 24)
        self.layout_main.setSpacing(20)

    def refresh(self) -> None:
        pass

    def confirm(self, kind: str = "item") -> bool:
        return QMessageBox.question(self, "Confirm deletion", f"Delete this {kind}? This cannot be undone.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes

    def alert(self, text: str) -> None:
        QMessageBox.warning(self, "Check your input", text)


def table_item(text, item_id: int | None = None) -> QTableWidgetItem:
    item = QTableWidgetItem(str(text))
    if item_id is not None:
        item.setData(Qt.UserRole, item_id)
    return item


def dialog_buttons(form: QDialog, handler) -> QDialogButtonBox:
    actions = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
    actions.accepted.connect(handler)
    actions.rejected.connect(form.reject)
    return actions


class TaskDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        data = data or {}
        self.setWindowTitle("Edit task" if data else "New task")
        self.setMinimumWidth(450)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 23, 24, 23)
        outer.addWidget(label("Focus on what matters", "sectionTitle"))
        form = QFormLayout()
        form.setSpacing(13)
        self.title = QLineEdit(data.get("title", ""))
        self.title.setPlaceholderText("e.g. Finish Python project")
        self.details = QPlainTextEdit(data.get("details", ""))
        self.details.setFixedHeight(84)
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        self.priority.setCurrentText(data.get("priority", "Medium"))
        self.category = QLineEdit(data.get("category", "General"))
        self.status = QComboBox()
        self.status.addItems(["Todo", "Doing", "Done"])
        self.status.setCurrentText(data.get("status", "Todo"))
        self.with_due = QCheckBox("Set due date")
        self.with_due.setChecked(bool(data.get("due_date")))
        self.due = QDateEdit()
        self.due.setCalendarPopup(True)
        self.due.setDisplayFormat("dd MMM yyyy")
        qdate = QDate.fromString(data.get("due_date", ""), "yyyy-MM-dd")
        self.due.setDate(qdate if qdate.isValid() else QDate.currentDate())
        self.due.setEnabled(self.with_due.isChecked())
        self.with_due.toggled.connect(self.due.setEnabled)
        form.addRow("Title", self.title)
        form.addRow("Details", self.details)
        form.addRow("Priority", self.priority)
        form.addRow("Category", self.category)
        form.addRow("Status", self.status)
        form.addRow("", self.with_due)
        form.addRow("Due", self.due)
        outer.addLayout(form)
        outer.addWidget(dialog_buttons(self, self._accept))

    def _accept(self):
        if not self.title.text().strip():
            QMessageBox.warning(self, "Missing title", "Please enter a task title.")
            return
        self.accept()

    def values(self) -> dict:
        return {
            "title": self.title.text().strip(), "details": self.details.toPlainText(),
            "priority": self.priority.currentText(), "category": self.category.text().strip(),
            "status": self.status.currentText(),
            "due_date": self.due.date().toString("yyyy-MM-dd") if self.with_due.isChecked() else "",
        }


class ExpenseDialog(QDialog):
    CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Education", "Health", "Entertainment", "Other"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log an expense")
        self.setMinimumWidth(430)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 23, 24, 23)
        lay.addWidget(label("Where did it go?", "sectionTitle"))
        form = QFormLayout()
        self.description = QLineEdit()
        self.description.setPlaceholderText("e.g. Groceries")
        self.amount = QDoubleSpinBox()
        self.amount.setDecimals(2)
        self.amount.setMaximum(999999999.99)
        self.amount.setMinimum(0.01)
        self.amount.setValue(100)
        self.amount.setPrefix(parent.main.currency + " " if hasattr(parent, "main") else "")
        self.category = QComboBox()
        self.category.addItems(self.CATEGORIES)
        self.day = QDateEdit()
        self.day.setDate(QDate.currentDate())
        self.day.setCalendarPopup(True)
        self.day.setDisplayFormat("dd MMM yyyy")
        self.note = QLineEdit()
        self.note.setPlaceholderText("Optional details")
        for name, widget in (("Description", self.description), ("Amount", self.amount),
                             ("Category", self.category), ("Date", self.day), ("Note", self.note)):
            form.addRow(name, widget)
        lay.addLayout(form)
        lay.addWidget(dialog_buttons(self, self._accept))

    def _accept(self):
        if not self.description.text().strip():
            QMessageBox.warning(self, "Missing description", "Add a short description.")
            return
        self.accept()

    def values(self) -> dict:
        return {
            "description": self.description.text().strip(), "cents": int(round(self.amount.value() * 100)),
            "category": self.category.currentText(), "day": self.day.date().toString("yyyy-MM-dd"),
            "note": self.note.text(),
        }


class PlanDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        data = data or {}
        self.setWindowTitle("Edit schedule" if data else "Schedule an activity")
        self.setMinimumWidth(450)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 23, 24, 23)
        lay.addWidget(label("Make time for it", "sectionTitle"))
        form = QFormLayout()
        self.title = QLineEdit(data.get("title", ""))
        self.title.setPlaceholderText("e.g. Study session")
        self.starts_at = QDateTimeEdit()
        self.starts_at.setCalendarPopup(True)
        self.starts_at.setDisplayFormat("dd MMM yyyy   hh:mm AP")
        start = QDateTime.fromString(data.get("starts_at", ""), "yyyy-MM-ddTHH:mm")
        self.starts_at.setDateTime(start if start.isValid() else QDateTime.currentDateTime().addSecs(3600))
        self.duration = QSpinBox()
        self.duration.setRange(5, 1440)
        self.duration.setSingleStep(5)
        self.duration.setSuffix(" min")
        self.duration.setValue(int(data.get("duration", 30)))
        self.details = QPlainTextEdit(data.get("details", ""))
        self.details.setFixedHeight(85)
        self.completed = QCheckBox("Completed")
        self.completed.setChecked(bool(data.get("completed", 0)))
        for title, field in (("Activity", self.title), ("Start", self.starts_at),
                             ("Duration", self.duration), ("Notes", self.details), ("", self.completed)):
            form.addRow(title, field)
        lay.addLayout(form)
        lay.addWidget(dialog_buttons(self, self._accept))

    def _accept(self):
        if not self.title.text().strip():
            QMessageBox.warning(self, "Missing activity", "Please enter an activity name.")
            return
        self.accept()

    def values(self) -> dict:
        return {"title": self.title.text().strip(),
                "starts_at": self.starts_at.dateTime().toString("yyyy-MM-ddTHH:mm"),
                "duration": self.duration.value(), "details": self.details.toPlainText(),
                "completed": self.completed.isChecked()}


class DashboardPage(Page):
    def __init__(self, store, main):
        super().__init__(store, main)
        self.layout_main.addWidget(section_header("Your workspace", "A clear view of your day, all in one place."))
        hero, hero_lay = card()
        head = QHBoxLayout()
        message = QVBoxLayout()
        self.greeting = label("Good to see you.", "sectionTitle")
        self.day_label = label("", "muted")
        message.addWidget(self.greeting)
        message.addWidget(self.day_label)
        head.addLayout(message, 1)
        head.addWidget(button("+ New task", "primary", lambda: self.main.navigate("Tasks", new=True)))
        head.addWidget(button("+ Quick note", "", lambda: self.main.navigate("Notes", new=True)))
        hero_lay.addLayout(head)
        self.layout_main.addWidget(hero)
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        self.stats = [
            MetricCard("Active tasks", foot="Stay focused on your priorities"),
            MetricCard("Tasks completed", foot="Progress adds up"),
            MetricCard("Habits today", foot="Your daily check-ins"),
            MetricCard("Focus minutes", foot="Deep work today"),
        ]
        for i, widget in enumerate(self.stats):
            grid.addWidget(widget, i // 4, i % 4)
        self.layout_main.addLayout(grid)
        lower = QHBoxLayout()
        lower.setSpacing(15)
        task_card, task_lay = card()
        task_lay.addWidget(label("Priority queue", "sectionTitle"))
        self.task_list = QVBoxLayout()
        task_lay.addLayout(self.task_list)
        task_lay.addStretch()
        lower.addWidget(task_card, 3)
        right, right_lay = card()
        right_lay.addWidget(label("Coming up", "sectionTitle"))
        self.plan_list = QVBoxLayout()
        right_lay.addLayout(self.plan_list)
        right_lay.addStretch()
        lower.addWidget(right, 2)
        self.layout_main.addLayout(lower, 1)
        links = QHBoxLayout()
        links.addWidget(button("Open planner  →", "", lambda: self.main.navigate("Planner")))
        links.addWidget(button("Track expenses  →", "", lambda: self.main.navigate("Expenses")))
        links.addWidget(button("Start focus session  →", "", lambda: self.main.navigate("Focus")))
        links.addStretch()
        self.layout_main.addLayout(links)

    def refresh(self):
        hour = datetime.now().hour
        self.greeting.setText("Good morning ✦" if hour < 12 else "Good afternoon ✦" if hour < 18 else "Good evening ✦")
        self.day_label.setText(date.today().strftime("%A, %d %B %Y") + "  ·  Small wins make big progress")
        s = self.store.overview()
        for widget, value in zip(self.stats, (s["active_tasks"], s["completed_tasks"],
                                               f'{s["habits_today"]} / {s["habits_total"]}',
                                               s["focus_today"])):
            widget.set_value(str(value))
        clear_layout(self.task_list)
        tasks = [t for t in self.store.tasks() if t["status"] != "Done"][:5]
        if not tasks:
            self.task_list.addWidget(label("No outstanding tasks. Enjoy the breathing room.", "muted"))
        for t in tasks:
            row = QHBoxLayout()
            row.addWidget(label("●", "accent"))
            row.addWidget(label(t["title"]), 1)
            row.addWidget(label(t["priority"], "mini"))
            self.task_list.addLayout(row)
        clear_layout(self.plan_list)
        plans = [p for p in self.store.plans() if not p["completed"] and p["starts_at"][:10] >= date.today().isoformat()][:4]
        if not plans:
            self.plan_list.addWidget(label("Your upcoming schedule is clear.", "muted"))
        for p in plans:
            holder = QVBoxLayout()
            holder.setSpacing(2)
            holder.addWidget(label(p["title"]))
            holder.addWidget(label(p["starts_at"].replace("T", "  •  "), "mini"))
            self.plan_list.addLayout(holder)


class TasksPage(Page):
    def __init__(self, store, main):
        super().__init__(store, main)
        self.layout_main.addWidget(section_header("Task management", "Organize priorities, set deadlines, and finish strong."))
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search tasks, descriptions, categories...")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search, 1)
        self.filter = QComboBox()
        self.filter.addItems(["All", "Todo", "Doing", "Done"])
        self.filter.currentTextChanged.connect(self.refresh)
        toolbar.addWidget(self.filter)
        toolbar.addWidget(button("+ Add task", "primary", self.new_task))
        self.layout_main.addLayout(toolbar)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["TASK", "PRIORITY", "CATEGORY", "DUE DATE", "STATUS"])
        style_table(self.table)
        self.table.doubleClicked.connect(self.edit_task)
        self.layout_main.addWidget(self.table, 1)
        actions = QHBoxLayout()
        actions.addWidget(button("Edit selected", "", self.edit_task))
        actions.addWidget(button("Advance status  →", "", self.advance_task))
        actions.addWidget(button("Delete", "danger", self.delete_task))
        actions.addStretch()
        actions.addWidget(label("Tip: double-click to edit", "mini"))
        self.layout_main.addLayout(actions)
        self.rows: dict[int, dict] = {}

    def current(self):
        row = self.table.currentRow()
        return self.rows.get(self.table.item(row, 0).data(Qt.UserRole)) if row >= 0 and self.table.item(row, 0) else None

    def refresh(self):
        rows = self.store.tasks(self.search.text(), self.filter.currentText())
        self.rows = {r["id"]: r for r in rows}
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            values = (r["title"], r["priority"], r["category"], r["due_date"] or "—", r["status"])
            for col, value in enumerate(values):
                self.table.setItem(i, col, table_item(value, r["id"] if col == 0 else None))

    def new_task(self):
        dialog = TaskDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.store.save_task(**dialog.values())
            self.refresh()
            self.main.status("Task created")

    def edit_task(self, *_):
        item = self.current()
        if item is None:
            return
        dialog = TaskDialog(self, item)
        if dialog.exec() == QDialog.Accepted:
            self.store.save_task(item_id=item["id"], **dialog.values())
            self.refresh()
            self.main.status("Task updated")

    def advance_task(self):
        item = self.current()
        if item is None:
            return
        next_status = {"Todo": "Doing", "Doing": "Done", "Done": "Todo"}[item["status"]]
        self.store.save_task(item_id=item["id"], title=item["title"], details=item["details"],
                             priority=item["priority"], category=item["category"],
                             due_date=item["due_date"], status=next_status)
        self.refresh()
        self.main.status(f"Moved to {next_status}")

    def delete_task(self):
        item = self.current()
        if item and self.confirm("task"):
            self.store.delete_task(item["id"])
            self.refresh()
            self.main.status("Task deleted")


class NotesPage(Page):
    def __init__(self, store, main):
        super().__init__(store, main)
        self.current_id = None
        self.loading = False
        self.dirty = False
        self.layout_main.addWidget(section_header("Notes studio", "Capture ideas, research, and anything worth remembering."))
        splitter = QSplitter(Qt.Horizontal)
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 4, 0)
        ll.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search your notes...")
        self.search.textChanged.connect(self.refresh)
        ll.addWidget(self.search)
        self.list = QListWidget()
        self.list.currentItemChanged.connect(self.load_selected)
        ll.addWidget(self.list, 1)
        ll.addWidget(button("+ New note", "primary", self.new_note))
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(12, 0, 0, 0)
        rl.setSpacing(10)
        self.title = QLineEdit()
        self.title.setPlaceholderText("Note title")
        self.title.setMinimumHeight(47)
        rl.addWidget(self.title)
        self.tags = QLineEdit()
        self.tags.setPlaceholderText("Tags (comma-separated)")
        rl.addWidget(self.tags)
        self.content = QPlainTextEdit()
        self.content.setPlaceholderText("Start writing something great...")
        rl.addWidget(self.content, 1)
        row = QHBoxLayout()
        row.addWidget(button("Save note", "primary", self.save_note))
        row.addWidget(button("Delete note", "danger", self.delete_note))
        row.addStretch()
        self.hint = label("Create a note or select one to begin", "mini")
        row.addWidget(self.hint)
        rl.addLayout(row)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([280, 700])
        splitter.setStretchFactor(1, 1)
        self.layout_main.addWidget(splitter, 1)
        for w in (self.title, self.tags):
            w.textEdited.connect(self.mark_dirty)
        self.content.textChanged.connect(self.mark_dirty)

    def mark_dirty(self, *_):
        if not self.loading:
            self.dirty = True
            self.hint.setText("Unsaved changes")

    def _persist_previous(self):
        # Auto-save valid, modified notes before selection changes.
        if self.dirty and self.title.text().strip():
            self.store.save_note(self.title.text(), self.content.toPlainText(),
                                 self.tags.text(), self.current_id)
            self.dirty = False

    def load_selected(self, new, _old):
        if self.loading:
            return
        self._persist_previous()
        if new is None:
            return
        item = new.data(Qt.UserRole)
        self.current_id = item["id"]
        self.loading = True
        self.title.setText(item["title"])
        self.tags.setText(item["tags"])
        self.content.setPlainText(item["content"])
        self.loading = False
        self.dirty = False
        self.hint.setText("Saved locally")

    def refresh(self):
        chosen = self.current_id
        self.loading = True
        self.list.clear()
        target = None
        for row in self.store.notes(self.search.text()):
            item = QListWidgetItem(f'{row["title"]}\n{row["tags"] or "No tags"}')
            item.setData(Qt.UserRole, row)
            self.list.addItem(item)
            if row["id"] == chosen:
                target = item
        if target is not None:
            self.list.setCurrentItem(target)
        self.loading = False

    def new_note(self):
        self._persist_previous()
        self.current_id = None
        self.loading = True
        self.list.setCurrentRow(-1)
        self.title.clear()
        self.tags.clear()
        self.content.clear()
        self.loading = False
        self.dirty = False
        self.hint.setText("New unsaved note")
        self.title.setFocus()

    def save_note(self):
        if not self.title.text().strip():
            self.alert("Please give your note a title before saving.")
            return
        self.current_id = self.store.save_note(self.title.text(), self.content.toPlainText(),
                                               self.tags.text(), self.current_id)
        self.dirty = False
        self.refresh()
        self.hint.setText("All changes saved")
        self.main.status("Note saved")

    def delete_note(self):
        if self.current_id is None:
            return
        if self.confirm("note"):
            self.store.delete_note(self.current_id)
            self.new_note()
            self.refresh()
            self.main.status("Note deleted")


class PlannerPage(Page):
    def __init__(self, store, main):
        super().__init__(store, main)
        self.layout_main.addWidget(section_header("Daily planner", "Protect time for your important activities."))
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search scheduled activities...")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search, 1)
        toolbar.addWidget(button("+ Schedule", "primary", self.add_plan))
        self.layout_main.addLayout(toolbar)
        split = QHBoxLayout()
        split.setSpacing(18)
        calendar_card, cl = card()
        calendar_card.setMaximumWidth(345)
        cl.addWidget(label("Calendar", "sectionTitle"))
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.refresh)
        cl.addWidget(self.calendar)
        self.date_filter = QCheckBox("Only selected day")
        self.date_filter.toggled.connect(self.refresh)
        cl.addWidget(self.date_filter)
        cl.addWidget(label("Select a day to filter your schedule.", "mini"))
        cl.addStretch()
        split.addWidget(calendar_card, 2)
        table_card, tl = card()
        tl.addWidget(label("Scheduled activities", "sectionTitle"))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ACTIVITY", "START", "DURATION", "STATE"])
        style_table(self.table)
        self.table.doubleClicked.connect(self.edit_plan)
        tl.addWidget(self.table, 1)
        row = QHBoxLayout()
        row.addWidget(button("Edit", "", self.edit_plan))
        row.addWidget(button("Toggle done", "", self.toggle_plan))
        row.addWidget(button("Delete", "danger", self.delete_plan))
        row.addStretch()
        tl.addLayout(row)
        split.addWidget(table_card, 5)
        self.layout_main.addLayout(split, 1)
        self.rows = {}

    def refresh(self):
        plans = self.store.plans(self.search.text())
        if self.date_filter.isChecked():
            chosen = self.calendar.selectedDate().toString("yyyy-MM-dd")
            plans = [p for p in plans if p["starts_at"].startswith(chosen)]
        self.rows = {p["id"]: p for p in plans}
        self.table.setRowCount(len(plans))
        for i, row in enumerate(plans):
            parts = (row["title"], row["starts_at"].replace("T", "  "),
                     f'{row["duration"]} min', "Complete" if row["completed"] else "Planned")
            for col, value in enumerate(parts):
                self.table.setItem(i, col, table_item(value, row["id"] if col == 0 else None))

    def selected(self):
        i = self.table.currentRow()
        return self.rows.get(self.table.item(i, 0).data(Qt.UserRole)) if i >= 0 and self.table.item(i, 0) else None

    def add_plan(self):
        dialog = PlanDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.store.save_plan(**dialog.values())
            self.refresh()
            self.main.status("Activity scheduled")

    def edit_plan(self, *_):
        current = self.selected()
        if current is None:
            return
        dialog = PlanDialog(self, current)
        if dialog.exec() == QDialog.Accepted:
            self.store.save_plan(item_id=current["id"], **dialog.values())
            self.refresh()
            self.main.status("Schedule updated")

    def toggle_plan(self):
        current = self.selected()
        if current:
            self.store.toggle_plan(current["id"])
            self.refresh()
            self.main.status("Schedule updated")

    def delete_plan(self):
        current = self.selected()
        if current and self.confirm("scheduled activity"):
            self.store.delete_plan(current["id"])
            self.refresh()
            self.main.status("Activity deleted")


class HabitsPage(Page):
    def __init__(self, store, main):
        super().__init__(store, main)
        self.layout_main.addWidget(section_header("Habit tracker", "Consistency beats intensity. Check in every day."))
        row = QHBoxLayout()
        self.name = QLineEdit()
        self.name.setPlaceholderText("New habit: read, stretch, practice Python...")
        self.name.returnPressed.connect(self.add_habit)
        row.addWidget(self.name, 1)
        row.addWidget(button("+ Add habit", "primary", self.add_habit))
        self.layout_main.addLayout(row)
        self.count = label("", "muted")
        self.layout_main.addWidget(self.count)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.inner = QWidget()
        self.stack = QVBoxLayout(self.inner)
        self.stack.setAlignment(Qt.AlignTop)
        self.stack.setSpacing(12)
        scroll.setWidget(self.inner)
        self.layout_main.addWidget(scroll, 1)

    def refresh(self):
        rows = self.store.habits()
        complete = sum(row["today_done"] for row in rows)
        self.count.setText(f"{complete} / {len(rows)} habits checked today  •  Your last 7 days are shown below")
        clear_layout(self.stack)
        if not rows:
            pane, lay = card()
            lay.addWidget(label("Build your first streak", "sectionTitle"))
            lay.addWidget(label("Add a habit above. Check it off every day to track your progress.", "muted"))
            self.stack.addWidget(pane)
        for r in rows:
            pane, lay = card()
            top = QHBoxLayout()
            col = QVBoxLayout()
            col.addWidget(label(r["name"], "sectionTitle"))
            col.addWidget(label(f'{r["streak"]}-day streak  ·  {r["week_done"]} of the last 7 days', "muted"))
            top.addLayout(col, 1)
            check = button("✓ Checked in" if r["today_done"] else "+ Check in", "primary" if not r["today_done"] else "")
            check.clicked.connect(lambda _=False, identifier=r["id"]: self.toggle(identifier))
            top.addWidget(check)
            remove = button("Remove", "danger")
            remove.clicked.connect(lambda _=False, identifier=r["id"]: self.delete(identifier))
            top.addWidget(remove)
            lay.addLayout(top)
            progress = QProgressBar()
            progress.setRange(0, 7)
            progress.setValue(r["week_done"])
            progress.setTextVisible(False)
            lay.addWidget(progress)
            self.stack.addWidget(pane)
        self.stack.addStretch()

    def add_habit(self):
        if not self.name.text().strip():
            self.alert("Enter a habit name.")
            return
        self.store.add_habit(self.name.text())
        self.name.clear()
        self.refresh()
        self.main.status("Habit created")

    def toggle(self, item_id):
        self.store.toggle_habit(item_id)
        self.refresh()
        self.main.status("Habit updated")

    def delete(self, item_id):
        if self.confirm("habit and its check-ins"):
            self.store.delete_habit(item_id)
            self.refresh()


class ExpensesPage(Page):
    def __init__(self, store, main):
        super().__init__(store, main)
        self.month = date.today().replace(day=1)
        self.layout_main.addWidget(section_header("Expense tracker", "Know where your money goes. No bank connection required."))
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search expenses...")
        self.search.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search, 1)
        toolbar.addWidget(button("←", "", lambda: self.shift_month(-1)))
        self.month_label = label("", "sectionTitle")
        toolbar.addWidget(self.month_label)
        toolbar.addWidget(button("→", "", lambda: self.shift_month(1)))
        toolbar.addWidget(button("+ Add expense", "primary", self.new_expense))
        self.layout_main.addLayout(toolbar)
        panel = QHBoxLayout()
        left, ll = card()
        ll.addWidget(label("Monthly spending", "muted"))
        self.total = label("", "metric")
        ll.addWidget(self.total)
        ll.addWidget(label("All expenses saved privately on this device", "mini"))
        panel.addWidget(left, 2)
        right, rl = card()
        rl.addWidget(label("Spending by category", "sectionTitle"))
        self.chart = BarChart()
        rl.addWidget(self.chart)
        panel.addWidget(right, 5)
        self.layout_main.addLayout(panel)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["DESCRIPTION", "CATEGORY", "DATE", "AMOUNT"])
        style_table(self.table)
        self.layout_main.addWidget(self.table, 1)
        bottom = QHBoxLayout()
        bottom.addWidget(button("Delete selected expense", "danger", self.delete_expense))
        bottom.addStretch()
        bottom.addWidget(label("Amounts use the currency selected in Settings", "mini"))
        self.layout_main.addLayout(bottom)

    def shift_month(self, increment: int):
        m = self.month.month + increment
        y = self.month.year
        if m > 12:
            m, y = 1, y + 1
        elif m < 1:
            m, y = 12, y - 1
        self.month = date(y, m, 1)
        self.refresh()

    def refresh(self):
        month = self.month.strftime("%Y-%m")
        self.month_label.setText(self.month.strftime("%b %Y"))
        rows = self.store.expenses(self.search.text(), month)
        breakdown = self.store.expense_breakdown(month)
        total = sum(i["cents"] for i in breakdown)
        self.total.setText(self.main.money(total))
        palette = colors(self.main.theme_name, self.main.accent_name)
        self.chart.set_data([(r["category"], r["cents"] / 100) for r in breakdown],
                            palette["accent"], palette["muted"])
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            fields = (row["description"], row["category"], row["day"], self.main.money(row["cents"]))
            for col, value in enumerate(fields):
                self.table.setItem(i, col, table_item(value, row["id"] if col == 0 else None))

    def new_expense(self):
        dialog = ExpenseDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.store.add_expense(**dialog.values())
            self.month = date.fromisoformat(dialog.values()["day"]).replace(day=1)
            self.refresh()
            self.main.status("Expense added")

    def delete_expense(self):
        i = self.table.currentRow()
        if i < 0 or self.table.item(i, 0) is None:
            return
        if self.confirm("expense"):
            self.store.delete_expense(self.table.item(i, 0).data(Qt.UserRole))
            self.refresh()
            self.main.status("Expense removed")


class FocusPage(Page):
    def __init__(self, store, main):
        super().__init__(store, main)
        self.duration = 25 * 60
        self.remaining = self.duration
        self.running = False
        self.was_started = False
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)
        self.layout_main.addWidget(section_header("Focus studio", "One focused session at a time. Create momentum."))
        self.layout_main.addStretch()
        frame, lay = card()
        frame.setMaximumWidth(650)
        frame.setMinimumHeight(410)
        self.layout_main.addWidget(frame, 0, Qt.AlignHCenter)
        lay.setContentsMargins(35, 30, 35, 30)
        lay.setSpacing(18)
        header = label("DEEP WORK MODE", "accent")
        header.setAlignment(Qt.AlignCenter)
        lay.addWidget(header)
        self.clock = label("25:00")
        self.clock.setAlignment(Qt.AlignCenter)
        self.clock.setStyleSheet("font-size: 78px; font-weight: 800; letter-spacing: 3px;")
        lay.addWidget(self.clock, 1)
        self.hint = label("Clear your mind. Choose your next focus block.", "muted")
        self.hint.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.hint)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        lay.addWidget(self.progress)
        presets = QHBoxLayout()
        presets.addStretch()
        for mins in (15, 25, 50):
            presets.addWidget(button(f"{mins} min", "", lambda _=False, m=mins: self.set_duration(m)))
        presets.addStretch()
        lay.addLayout(presets)
        actions = QHBoxLayout()
        self.start_button = button("▶ Start focus", "primary", self.start_pause)
        actions.addWidget(self.start_button, 1)
        actions.addWidget(button("↺ Reset", "", self.reset))
        lay.addLayout(actions)
        self.layout_main.addStretch()
        self.today = label("", "muted")
        self.today.setAlignment(Qt.AlignCenter)
        self.layout_main.addWidget(self.today)

    def set_duration(self, minutes):
        if self.running:
            self.alert("Pause or reset your active session before changing duration.")
            return
        self.duration = minutes * 60
        self.remaining = self.duration
        self.was_started = False
        self.hint.setText(f"{minutes}-minute focus block ready")
        self._render()

    def start_pause(self):
        if self.running:
            self.running = False
            self.timer.stop()
            self.hint.setText("Paused — resume when ready")
        else:
            self.running = True
            self.was_started = True
            self.timer.start()
            self.hint.setText("Stay with the task. You've got this.")
        self._render()

    def tick(self):
        if not self.running:
            return
        self.remaining = max(0, self.remaining - 1)
        self._render()
        if self.remaining == 0:
            self.timer.stop()
            self.running = False
            self.was_started = False
            self.store.record_focus(self.duration // 60)
            self.hint.setText("Session complete! Your focus time is logged.")
            self._render()
            self.refresh()
            QMessageBox.information(self, "Focus complete", "Session complete! Great work.")

    def reset(self):
        self.timer.stop()
        self.running = False
        self.was_started = False
        self.remaining = self.duration
        self.hint.setText("Session reset and ready")
        self._render()

    def _render(self):
        mm, ss = divmod(self.remaining, 60)
        self.clock.setText(f"{mm:02d}:{ss:02d}")
        self.progress.setValue(int((self.duration - self.remaining) * 100 / self.duration))
        self.start_button.setText("Ⅱ Pause" if self.running else "▶ Resume" if self.was_started else "▶ Start focus")

    def refresh(self):
        self.today.setText(f"You've completed {self.store.focus_today()} minutes of focused work today")


class SettingsPage(Page):
    def __init__(self, store, main):
        super().__init__(store, main)
        self.layout_main.addWidget(section_header("Preferences", "Make the workspace feel like yours, and keep your data safe."))
        visual, vl = card()
        vl.addWidget(label("Appearance", "sectionTitle"))
        row = QHBoxLayout()
        self.theme = QComboBox()
        self.theme.addItems(["Midnight", "Daylight"])
        self.accent = QComboBox()
        self.accent.addItems(["Violet", "Cyan", "Coral", "Emerald"])
        self.currency = QComboBox()
        self.currency.addItems(["PKR", "USD", "EUR", "GBP", "INR"])
        for title, widget in (("Theme", self.theme), ("Accent", self.accent), ("Currency", self.currency)):
            block = QVBoxLayout()
            block.addWidget(label(title, "muted"))
            block.addWidget(widget)
            row.addLayout(block, 1)
        vl.addLayout(row)
        vl.addWidget(label("Changes apply immediately and are remembered on this device.", "mini"))
        self.layout_main.addWidget(visual)
        data, dl = card()
        dl.addWidget(label("Your data", "sectionTitle"))
        dl.addWidget(label("Everything stays on this computer. No sign-in, cloud sync, or tracking.", "muted"))
        self.folder_hint = label(str(self.store.path), "mini")
        self.folder_hint.setTextInteractionFlags(Qt.TextSelectableByMouse)
        dl.addWidget(self.folder_hint)
        actions = QHBoxLayout()
        actions.addWidget(button("Backup database", "primary", self.backup))
        actions.addWidget(button("Export CSV files", "", self.export_csv))
        actions.addWidget(button("Open data folder", "", self.open_folder))
        actions.addStretch()
        dl.addLayout(actions)
        self.layout_main.addWidget(data)
        info, il = card()
        il.addWidget(label("About MAH DailyDesk", "sectionTitle"))
        il.addWidget(label("Version 1.0.0  •  Created with Python, PySide6, and SQLite", "muted"))
        il.addWidget(label("Shortcuts: Ctrl+1 through Ctrl+8 switch sections. Ctrl+N opens a new task.", "mini"))
        self.layout_main.addWidget(info)
        self.layout_main.addStretch()
        self.theme.currentTextChanged.connect(self.change)
        self.accent.currentTextChanged.connect(self.change)
        self.currency.currentTextChanged.connect(self.change)

    def refresh(self):
        for combo, value in ((self.theme, self.main.theme_name),
                             (self.accent, self.main.accent_name), (self.currency, self.main.currency)):
            with QSignalBlocker(combo):
                combo.setCurrentText(value)

    def change(self, *_):
        self.main.apply_preferences(self.theme.currentText(), self.accent.currentText(), self.currency.currentText())

    def backup(self):
        suggested = str(Path.home() / f'dailydesk-backup-{date.today().isoformat()}.sqlite3')
        destination, _ = QFileDialog.getSaveFileName(self, "Backup database", suggested, "SQLite database (*.sqlite3)")
        if not destination:
            return
        try:
            target = self.store.backup(destination)
        except (OSError, ValueError) as err:
            self.alert(f"Backup failed: {err}")
            return
        QMessageBox.information(self, "Backup saved", f"Database backed up to:\n{target}")

    def export_csv(self):
        folder = QFileDialog.getExistingDirectory(self, "Select CSV export folder", str(Path.home()))
        if not folder:
            return
        try:
            paths = self.store.export_csv(folder)
        except OSError as err:
            self.alert(f"Export failed: {err}")
            return
        QMessageBox.information(self, "Export complete", f"Exported {len(paths)} CSV files to:\n{folder}")

    def open_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.store.path.parent)))