"""Core regression tests. These intentionally run without Qt installed."""
from __future__ import annotations

import csv
import sqlite3
from datetime import date, timedelta

import pytest

from dailydesk.core.storage import Store


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "test.sqlite3")
    yield s
    s.close()


def test_fresh_database_has_zeroed_overview(store):
    overview = store.overview()
    assert overview["active_tasks"] == 0
    assert overview["notes"] == 0
    assert overview["expense_month_cents"] == 0
    assert overview["focus_today"] == 0


def test_task_add_search_update_filter_delete(store):
    item_id = store.save_task("Finish the launch", "Review everything", "High", "Dev", "2026-11-20")
    assert store.tasks("launch")[0]["id"] == item_id
    assert store.tasks("Review")[0]["priority"] == "High"
    assert store.tasks(status="Done") == []
    store.save_task(title="Publish release", priority="Medium", status="Done", item_id=item_id)
    assert store.tasks(status="Done")[0]["title"] == "Publish release"
    assert store.overview()["completed_tasks"] == 1
    store.delete_task(item_id)
    assert store.tasks() == []


def test_task_validations_and_sql_input(store):
    with pytest.raises(ValueError):
        store.save_task("  ")
    with pytest.raises(ValueError):
        store.save_task("Valid", status="Unknown")
    store.save_task("' OR 1=1 --")
    assert len(store.tasks("' OR 1=1 --")) == 1
    assert len(store.tasks("no such record")) == 0


def test_notes_create_update_and_search(store):
    item_id = store.save_note("Ideas", "Make a useful program", "python,gui")
    assert store.notes("useful")[0]["id"] == item_id
    assert store.notes("python")[0]["title"] == "Ideas"
    store.save_note("Ideas v2", "New content", item_id=item_id)
    assert store.notes()[0]["content"] == "New content"
    store.delete_note(item_id)
    assert store.notes() == []


def test_habit_checkins_and_streak(store):
    habit = store.add_habit("Read 10 pages")
    today = date.today()
    assert store.toggle_habit(habit, (today - timedelta(days=1)).isoformat()) is True
    assert store.toggle_habit(habit) is True
    r = store.habits()[0]
    assert r["today_done"] is True
    assert r["streak"] == 2
    assert r["week_done"] == 2
    assert store.toggle_habit(habit) is False
    assert store.habits()[0]["streak"] == 1
    store.delete_habit(habit)
    assert store.habits() == []
    assert store.db.execute("SELECT count(*) FROM habit_entries").fetchone()[0] == 0


def test_expenses_are_integral_cents_and_month_filtered(store):
    store.add_expense("Stationery", 1299, "Education", "2026-10-22")
    extra = store.add_expense("Tea", 175, "Food", "2026-11-02")
    assert len(store.expenses(month="2026-11")) == 1
    assert store.expense_breakdown("2026-10")[0]["cents"] == 1299
    assert store.expenses("Tea")[0]["cents"] == 175
    store.delete_expense(extra)
    assert store.expenses(month="2026-11") == []
    with pytest.raises(ValueError):
        store.add_expense("Bad value", 0)


def test_planner_update_toggle_delete(store):
    item_id = store.save_plan("Meeting", "2026-11-21T14:30", duration=45)
    assert store.plans()[0]["duration"] == 45
    store.toggle_plan(item_id)
    assert store.plans()[0]["completed"] == 1
    store.save_plan("Meeting updated", "2026-11-22T14:30", item_id=item_id)
    assert store.plans("updated")[0]["title"] == "Meeting updated"
    store.delete_plan(item_id)
    assert store.plans() == []
    with pytest.raises(ValueError):
        store.save_plan("Invalid", "not-a-date")


def test_focus_sessions_and_preferences(store):
    with pytest.raises(ValueError):
        store.record_focus(0)
    store.record_focus(25)
    store.record_focus(15)
    assert store.focus_today() == 40
    assert store.get_pref("color", "unset") == "unset"
    store.set_pref("color", "Cyan")
    store.set_pref("color", "Coral")
    assert store.get_pref("color") == "Coral"


def test_backup_and_csv_export(store, tmp_path):
    store.save_note("Private", "Some thoughts")
    store.add_expense("Rent", 100000, "Bills")
    backup = store.backup(tmp_path / "backup" / "copy.sqlite3")
    with sqlite3.connect(backup) as conn:
        assert conn.execute("SELECT count(*) FROM notes").fetchone()[0] == 1
    paths = store.export_csv(tmp_path / "exports")
    assert len(paths) == 7
    with (tmp_path / "exports" / "notes.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
        assert rows[0]["title"] == "Private"
    with pytest.raises(ValueError):
        store.backup(store.path)


def test_csv_export_neutralizes_spreadsheet_formula_payloads(store, tmp_path):
    store.save_note("=1+1", "+SUM(A1:A2)")
    store.export_csv(tmp_path / "csv")
    with (tmp_path / "csv" / "notes.csv").open(encoding="utf-8-sig", newline="") as file:
        entry = list(csv.DictReader(file))[0]
        assert entry["title"] == "'=1+1"
        assert entry["content"] == "'+SUM(A1:A2)"