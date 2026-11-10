"""Local, offline-first SQLite persistence for MAH DailyDesk.

All SQL parameters are bound (never interpolated from user input). User-generated
content stays outside the installation/repository folder by default.
"""
from __future__ import annotations

import csv
import os
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

APP_NAME = "MAH DailyDesk"


def safe_spreadsheet_value(value: Any) -> Any:
    """Neutralize spreadsheet-formula prefixes in exported user-entered strings."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


def data_directory() -> Path:
    """Return an OS-appropriate per-user writable application data directory."""
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        root = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return root / "MAH-DailyDesk"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Store:
    """Database façade used by UI pages and independently unit-testable."""

    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path is not None else data_directory() / "dailydesk.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if path is None and os.name != "nt":
            # Private by default for notes, budgets and other personal records.
            self.path.parent.chmod(0o700)
        self.db = sqlite3.connect(str(self.path))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.execute("PRAGMA busy_timeout = 3000")
        self.db.execute("PRAGMA journal_mode = WAL")
        self._init_db()

    def close(self) -> None:
        self.db.close()

    def _init_db(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, details TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'Medium', category TEXT NOT NULL DEFAULT 'General',
                due_date TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Todo',
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS habit_entries (
                habit_id INTEGER NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
                day TEXT NOT NULL, PRIMARY KEY (habit_id, day)
            );
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY, description TEXT NOT NULL, cents INTEGER NOT NULL CHECK(cents > 0),
                category TEXT NOT NULL, day TEXT NOT NULL, note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY, title TEXT NOT NULL, details TEXT NOT NULL DEFAULT '',
                starts_at TEXT NOT NULL, duration INTEGER NOT NULL DEFAULT 30,
                completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1))
            );
            CREATE TABLE IF NOT EXISTS focus_sessions (
                id INTEGER PRIMARY KEY, minutes INTEGER NOT NULL CHECK(minutes > 0),
                finished_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY, value TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_expense_day ON expenses(day);
            CREATE INDEX IF NOT EXISTS idx_plan_start ON plans(starts_at);
            """
        )
        self.db.commit()

    def _fetchall(self, sql: str, args: tuple = ()) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.execute(sql, args).fetchall()]

    def _fetchone(self, sql: str, args: tuple = ()) -> dict[str, Any] | None:
        row = self.db.execute(sql, args).fetchone()
        return dict(row) if row is not None else None

    def _execute(self, sql: str, args: tuple = ()) -> int:
        with self.db:
            return int(self.db.execute(sql, args).lastrowid)

    # Tasks
    def tasks(self, query: str = "", status: str = "All") -> list[dict[str, Any]]:
        clause = " WHERE (title LIKE ? OR details LIKE ? OR category LIKE ?)"
        like = f"%{query.strip()}%"
        args: tuple[Any, ...] = (like, like, like)
        if status != "All":
            clause += " AND status = ?"
            args += (status,)
        return self._fetchall(
            "SELECT * FROM tasks" + clause +
            " ORDER BY CASE status WHEN 'Doing' THEN 0 WHEN 'Todo' THEN 1 ELSE 2 END, "
            "CASE priority WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 ELSE 2 END, "
            "CASE WHEN due_date='' THEN 1 ELSE 0 END, due_date, id DESC", args,
        )

    def save_task(self, title: str, details: str = "", priority: str = "Medium",
                  category: str = "General", due_date: str = "", status: str = "Todo",
                  item_id: int | None = None) -> int:
        if not title.strip():
            raise ValueError("Task title is required")
        if status not in {"Todo", "Doing", "Done"} or priority not in {"Low", "Medium", "High"}:
            raise ValueError("Unsupported task state")
        t = now_iso()
        if item_id is None:
            return self._execute(
                "INSERT INTO tasks (title,details,priority,category,due_date,status,created_at,updated_at) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (title.strip(), details, priority, category or "General", due_date, status, t, t),
            )
        self._execute(
            "UPDATE tasks SET title=?,details=?,priority=?,category=?,due_date=?,status=?,updated_at=? "
            "WHERE id=?", (title.strip(), details, priority, category or "General", due_date, status, t, item_id),
        )
        return item_id

    def delete_task(self, item_id: int) -> None:
        self._execute("DELETE FROM tasks WHERE id=?", (item_id,))

    # Notes
    def notes(self, query: str = "") -> list[dict[str, Any]]:
        like = f"%{query.strip()}%"
        return self._fetchall(
            "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? "
            "ORDER BY updated_at DESC, id DESC", (like, like, like),
        )

    def save_note(self, title: str, content: str = "", tags: str = "", item_id: int | None = None) -> int:
        if not title.strip():
            raise ValueError("Note title is required")
        t = now_iso()
        if item_id is None:
            return self._execute("INSERT INTO notes (title,content,tags,created_at,updated_at) VALUES (?,?,?,?,?)",
                                 (title.strip(), content, tags.strip(), t, t))
        self._execute("UPDATE notes SET title=?,content=?,tags=?,updated_at=? WHERE id=?",
                      (title.strip(), content, tags.strip(), t, item_id))
        return item_id

    def delete_note(self, item_id: int) -> None:
        self._execute("DELETE FROM notes WHERE id=?", (item_id,))

    # Habits
    def habits(self) -> list[dict[str, Any]]:
        rows = self._fetchall("SELECT * FROM habits ORDER BY id DESC")
        for row in rows:
            entries = {r["day"] for r in self._fetchall("SELECT day FROM habit_entries WHERE habit_id=?", (row["id"],))}
            today = date.today()
            row["today_done"] = today.isoformat() in entries
            row["week_done"] = sum((today - timedelta(days=d)).isoformat() in entries for d in range(7))
            start = today if today.isoformat() in entries else today - timedelta(days=1)
            streak = 0
            while (start - timedelta(days=streak)).isoformat() in entries:
                streak += 1
            row["streak"] = streak
        return rows

    def add_habit(self, name: str) -> int:
        if not name.strip():
            raise ValueError("Habit name is required")
        return self._execute("INSERT INTO habits (name,created_at) VALUES (?,?)", (name.strip(), now_iso()))

    def toggle_habit(self, item_id: int, day: str | None = None) -> bool:
        day = day or date.today().isoformat()
        if self._fetchone("SELECT 1 AS found FROM habit_entries WHERE habit_id=? AND day=?", (item_id, day)):
            self._execute("DELETE FROM habit_entries WHERE habit_id=? AND day=?", (item_id, day))
            return False
        self._execute("INSERT INTO habit_entries (habit_id,day) VALUES (?,?)", (item_id, day))
        return True

    def delete_habit(self, item_id: int) -> None:
        self._execute("DELETE FROM habits WHERE id=?", (item_id,))

    # Expenses, stored in integral cents to prevent rounding drift.
    def expenses(self, query: str = "", month: str = "") -> list[dict[str, Any]]:
        like = f"%{query.strip()}%"
        if month:
            return self._fetchall(
                "SELECT * FROM expenses WHERE (description LIKE ? OR category LIKE ?) AND day LIKE ? "
                "ORDER BY day DESC,id DESC", (like, like, month + "%"),
            )
        return self._fetchall(
            "SELECT * FROM expenses WHERE description LIKE ? OR category LIKE ? ORDER BY day DESC,id DESC",
            (like, like),
        )

    def add_expense(self, description: str, cents: int, category: str = "Other",
                    day: str | None = None, note: str = "") -> int:
        if not description.strip() or cents <= 0:
            raise ValueError("Expense description and positive amount are required")
        return self._execute(
            "INSERT INTO expenses (description,cents,category,day,note,created_at) VALUES (?,?,?,?,?,?)",
            (description.strip(), int(cents), category, day or date.today().isoformat(), note, now_iso()),
        )

    def delete_expense(self, item_id: int) -> None:
        self._execute("DELETE FROM expenses WHERE id=?", (item_id,))

    def expense_breakdown(self, month: str) -> list[dict[str, Any]]:
        return self._fetchall(
            "SELECT category, SUM(cents) AS cents FROM expenses WHERE day LIKE ? "
            "GROUP BY category ORDER BY cents DESC", (month + "%",),
        )

    # Planner
    def plans(self, query: str = "") -> list[dict[str, Any]]:
        like = f"%{query.strip()}%"
        return self._fetchall(
            "SELECT * FROM plans WHERE title LIKE ? OR details LIKE ? "
            "ORDER BY completed ASC,starts_at ASC,id DESC", (like, like),
        )

    def save_plan(self, title: str, starts_at: str, duration: int = 30,
                  details: str = "", completed: bool = False, item_id: int | None = None) -> int:
        if not title.strip() or duration <= 0:
            raise ValueError("Plan title and positive duration are required")
        datetime.fromisoformat(starts_at)  # Validate before inserting.
        if item_id is None:
            return self._execute(
                "INSERT INTO plans (title,starts_at,duration,details,completed) VALUES (?,?,?,?,?)",
                (title.strip(), starts_at, duration, details, int(completed)),
            )
        self._execute(
            "UPDATE plans SET title=?,starts_at=?,duration=?,details=?,completed=? WHERE id=?",
            (title.strip(), starts_at, duration, details, int(completed), item_id),
        )
        return item_id

    def delete_plan(self, item_id: int) -> None:
        self._execute("DELETE FROM plans WHERE id=?", (item_id,))

    def toggle_plan(self, item_id: int) -> None:
        self._execute("UPDATE plans SET completed=1-completed WHERE id=?", (item_id,))

    # Focus and preferences
    def record_focus(self, minutes: int) -> int:
        if minutes <= 0:
            raise ValueError("Focus minutes must be positive")
        return self._execute("INSERT INTO focus_sessions (minutes,finished_at) VALUES (?,?)",
                             (minutes, now_iso()))

    def focus_today(self) -> int:
        row = self._fetchone("SELECT COALESCE(SUM(minutes),0) AS total FROM focus_sessions WHERE finished_at LIKE ?",
                             (date.today().isoformat() + "%",))
        return int(row["total"]) if row else 0

    def get_pref(self, key: str, default: str = "") -> str:
        r = self._fetchone("SELECT value FROM preferences WHERE key=?", (key,))
        return str(r["value"]) if r is not None else default

    def set_pref(self, key: str, value: str) -> None:
        self._execute("INSERT INTO preferences (key,value) VALUES (?,?) "
                      "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def overview(self) -> dict[str, int]:
        today = date.today().isoformat()
        month = today[:7]
        q = lambda sql, args=(): int(self.db.execute(sql, args).fetchone()[0])
        return {
            "active_tasks": q("SELECT count(*) FROM tasks WHERE status != 'Done'"),
            "completed_tasks": q("SELECT count(*) FROM tasks WHERE status = 'Done'"),
            "notes": q("SELECT count(*) FROM notes"),
            "habits_today": q("SELECT count(*) FROM habit_entries WHERE day=?", (today,)),
            "habits_total": q("SELECT count(*) FROM habits"),
            "expense_month_cents": q("SELECT COALESCE(sum(cents),0) FROM expenses WHERE day LIKE ?", (month + "%",)),
            "upcoming_plans": q("SELECT count(*) FROM plans WHERE completed=0 AND starts_at>=?", (today,)),
            "focus_today": self.focus_today(),
        }

    def backup(self, destination: Path | str) -> Path:
        """Consistent database backup, even with SQLite WAL enabled."""
        target = Path(destination)
        if target.resolve() == self.path.resolve():
            raise ValueError("Backup destination must differ from live database")
        target.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(target)) as backup_db:
            self.db.backup(backup_db)
        return target

    def export_csv(self, folder: Path | str) -> list[Path]:
        root = Path(folder)
        root.mkdir(parents=True, exist_ok=True)
        tables = ("tasks", "notes", "habits", "habit_entries", "expenses", "plans", "focus_sessions")
        exported: list[Path] = []
        for table in tables:  # Identifiers are hardcoded, never user-supplied.
            cursor = self.db.execute(f"SELECT * FROM {table}")
            path = root / f"{table}.csv"
            with path.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.writer(handle)
                writer.writerow([column[0] for column in cursor.description])
                for row in cursor:
                    writer.writerow([safe_spreadsheet_value(cell) for cell in row])
            exported.append(path)
        return exported