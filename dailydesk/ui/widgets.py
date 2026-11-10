"""Reusable visual components and lightweight Qt-painted analytics."""
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QTableWidget, QHeaderView, QPushButton,
    QVBoxLayout, QWidget, QGraphicsDropShadowEffect
)


def label(text: str, kind: str = "", parent: QWidget | None = None) -> QLabel:
    item = QLabel(text, parent)
    if kind:
        item.setObjectName(kind)
    item.setWordWrap(True)
    return item


def button(text: str, kind: str = "", callback=None) -> QPushButton:
    item = QPushButton(text)
    item.setCursor(Qt.PointingHandCursor)
    if kind:
        item.setObjectName(kind)
    if callback is not None:
        item.clicked.connect(callback)
    return item


def card() -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(22, 19, 22, 19)
    layout.setSpacing(12)
    return frame, layout


def section_header(title: str, detail: str = "") -> QWidget:
    root = QWidget()
    lay = QVBoxLayout(root)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(5)
    lay.addWidget(label(title, "headline"))
    if detail:
        lay.addWidget(label(detail, "subtitle"))
    return root


def style_table(table: QTableWidget) -> None:
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setSelectionMode(QTableWidget.SingleSelection)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(48)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setShowGrid(False)


def clear_layout(layout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            clear_layout(item.layout())


class MetricCard(QFrame):
    def __init__(self, caption: str, value: str = "—", foot: str = ""):
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)
        layout.addWidget(label(caption, "muted"))
        self.value = label(value, "metric")
        layout.addWidget(self.value)
        layout.addWidget(label(foot, "mini"))
        self.setMinimumHeight(131)

    def set_value(self, value: str) -> None:
        self.value.setText(value)


class BarChart(QWidget):
    """Simple no-dependency interactive chart with bar hover tooltips."""
    def __init__(self):
        super().__init__()
        self.points: list[tuple[str, float]] = []
        self.accent = QColor("#9B8DFF")
        self.muted = QColor("#9DAAC3")
        self.setMinimumHeight(188)
        self.setMouseTracking(True)
        self._bounds: list[tuple[QRectF, str]] = []

    def set_data(self, points: list[tuple[str, float]], accent: str, muted: str) -> None:
        self.points = points
        self.accent = QColor(accent)
        self.muted = QColor(muted)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        self._bounds = []
        if not self.points:
            painter.setPen(self.muted)
            painter.drawText(self.rect(), Qt.AlignCenter, "Your chart will appear here")
            return
        margin_x = 18
        top = 14
        bottom = 29
        width = max(1, self.width() - 2 * margin_x)
        height = max(1, self.height() - bottom - top)
        maximum = max(1.0, max(v for _, v in self.points))
        slot = width / len(self.points)
        for i, (name, val) in enumerate(self.points):
            bar_w = min(56.0, slot * 0.56)
            bar_h = max(3, height * max(0, val) / maximum)
            x = margin_x + i * slot + (slot - bar_w) / 2
            y = top + height - bar_h
            rect = QRectF(x, y, bar_w, bar_h)
            self._bounds.append((rect, f"{name}: {val:,.2f}"))
            color = QColor(self.accent)
            color.setAlpha(225 if val else 80)
            painter.setBrush(color)
            painter.drawRoundedRect(rect, 6, 6)
            painter.setPen(self.muted)
            font = QFont("Segoe UI", 9)
            painter.setFont(font)
            painter.drawText(QRectF(margin_x + i * slot, self.height() - 24, slot, 20), Qt.AlignCenter, name[:11])
            painter.setPen(Qt.NoPen)
        painter.end()

    def mouseMoveEvent(self, event) -> None:
        from PySide6.QtWidgets import QToolTip
        for bounds, tip in self._bounds:
            if bounds.contains(event.position()):
                QToolTip.showText(event.globalPosition().toPoint(), tip, self)
                return
        QToolTip.hideText()


def add_shadow(widget: QWidget) -> None:
    """Optional subtle elevation used only on large hero surfaces."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(18)
    shadow.setOffset(0, 5)
    shadow.setColor(QColor(0, 0, 0, 32))
    widget.setGraphicsEffect(shadow)