"""A calm, high-contrast design system with accessible light and dark themes."""
from __future__ import annotations

PALETTES = {
    "Midnight": {
        "bg": "#0B1020", "panel": "#121A2B", "panel2": "#192338",
        "hover": "#26334C", "border": "#2B3852", "text": "#EDF2FF",
        "muted": "#9DAAC3", "soft": "#697891", "good": "#51D4AA", "danger": "#F77D90",
    },
    "Daylight": {
        "bg": "#F1F5FB", "panel": "#FFFFFF", "panel2": "#E9EFF8",
        "hover": "#DCE6F3", "border": "#D6E0EE", "text": "#19263D",
        "muted": "#5B6B82", "soft": "#8190A2", "good": "#17805C", "danger": "#BD3454",
    },
}
ACCENTS = {"Violet": "#9B8DFF", "Cyan": "#36CFEA", "Coral": "#FF718B", "Emerald": "#48CFA5"}


def colors(theme: str, accent: str) -> dict[str, str]:
    return {**PALETTES.get(theme, PALETTES["Midnight"]), "accent": ACCENTS.get(accent, ACCENTS["Violet"])}


def stylesheet(theme: str, accent: str) -> str:
    c = colors(theme, accent)
    return """
    QWidget { font-family: 'Segoe UI', 'Inter', Arial; font-size: 13px; color: %(text)s; }
    QMainWindow, QWidget#appRoot { background: %(bg)s; }
    QFrame#sidebar, QFrame#surface, QFrame#card, QFrame#toolbar, QFrame#dialogCard {
        background: %(panel)s; border: 1px solid %(border)s; border-radius: 17px;
    }
    QFrame#sidebar { border-radius: 0px; border-top: 0px; border-bottom: 0px; border-left: 0px; }
    QLabel#brand { font-size: 21px; font-weight: 800; letter-spacing: 0.5px; }
    QLabel#headline { font-size: 29px; font-weight: 800; }
    QLabel#sectionTitle { font-size: 18px; font-weight: 700; }
    QLabel#metric { font-size: 30px; font-weight: 800; }
    QLabel#muted, QLabel#subtitle, QLabel#helper { color: %(muted)s; }
    QLabel#mini { color: %(soft)s; font-size: 11px; }
    QLabel#accent { color: %(accent)s; font-weight: 700; }
    QPushButton { background: %(panel2)s; border: 1px solid %(border)s; border-radius: 11px;
        padding: 9px 15px; font-weight: 600; }
    QPushButton:hover { background: %(hover)s; border-color: %(accent)s; }
    QPushButton:pressed { background: %(border)s; }
    QPushButton:disabled { color: %(soft)s; background: %(panel)s; }
    QPushButton#primary { background: %(accent)s; color: %(bg)s; border: 1px solid %(accent)s; }
    QPushButton#primary:hover { background: %(text)s; color: %(bg)s; border-color: %(text)s; }
    QPushButton#danger { color: %(danger)s; }
    QPushButton#nav { background: transparent; text-align: left; border: 1px solid transparent;
        padding: 12px 17px; border-radius: 12px; font-size: 13px; color: %(muted)s; }
    QPushButton#nav:hover { background: %(panel2)s; color: %(text)s; }
    QPushButton#nav[active="true"] { background: %(panel2)s; color: %(accent)s; border-color: %(border)s; }
    QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QDateEdit, QDateTimeEdit { background: %(panel2)s; border: 1px solid %(border)s;
        border-radius: 10px; padding: 9px; selection-background-color: %(accent)s;
        selection-color: %(bg)s; }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
    QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QDateTimeEdit:focus {
        border: 1px solid %(accent)s; }
    QPlainTextEdit { padding: 13px; }
    QComboBox::drop-down, QDateEdit::drop-down, QDateTimeEdit::drop-down {
        border: 0px; width: 24px; }
    QComboBox QAbstractItemView { background: %(panel)s; color: %(text)s;
        selection-background-color: %(hover)s; border: 1px solid %(border)s; }
    QTableWidget, QListWidget { background: %(panel)s; alternate-background-color: %(panel2)s;
        border: 1px solid %(border)s; border-radius: 12px; outline: none; padding: 5px;
        gridline-color: %(border)s; }
    QTableWidget::item, QListWidget::item { padding: 8px; border-radius: 5px; }
    QTableWidget::item:selected, QListWidget::item:selected { background: %(hover)s; color: %(text)s; }
    QHeaderView::section { background: %(panel)s; color: %(muted)s; border: 0px;
        border-bottom: 1px solid %(border)s; padding: 12px; font-weight: 700; }
    QScrollArea { border: 0px; background: transparent; }
    QScrollBar:vertical { background: transparent; width: 9px; margin: 1px; }
    QScrollBar::handle:vertical { background: %(border)s; border-radius: 4px; min-height: 30px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QProgressBar { background: %(panel2)s; border: 0px; border-radius: 7px; height: 11px; text-align: center; }
    QProgressBar::chunk { background: %(accent)s; border-radius: 7px; }
    QCalendarWidget { background: %(panel)s; }
    QCalendarWidget QToolButton { background: %(panel2)s; border: 0; }
    QCalendarWidget QAbstractItemView { background: %(panel)s; color: %(text)s;
        selection-background-color: %(accent)s; selection-color: %(bg)s; }
    QCheckBox { spacing: 8px; }
    QCheckBox::indicator { width: 17px; height: 17px; }
    QDialog { background: %(bg)s; }
    QToolTip { background: %(panel2)s; border: 1px solid %(accent)s; color: %(text)s; padding: 6px; }
    """ % c