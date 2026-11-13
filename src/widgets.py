import math
from PyQt5.QtWidgets import (QPushButton, QComboBox, QAbstractItemView, 
                             QListView, QStyledItemDelegate, QStyle)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, pyqtProperty
from PyQt5.QtGui import QPainter, QColor, QBrush, QPainterPath, QPen
from .theme import COLORS
class RippleButton(QPushButton):
    def __init__(self, text="", parent=None, border_radius=10):
        super().__init__(text, parent)
        self._radius = 0
        self._click_pos = QPoint()
        self._max_radius = 0
        self._border_radius = border_radius
        self._animation = QPropertyAnimation(self, b"radius")
        self._animation.setDuration(400)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
    def get_radius(self): return self._radius
    def set_radius(self, radius):
        self._radius = radius
        self.update()
    radius = pyqtProperty(float, get_radius, set_radius)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._click_pos = event.pos()
            self._max_radius = max(
                math.hypot(self._click_pos.x(), self._click_pos.y()),
                math.hypot(self.width() - self._click_pos.x(), self._click_pos.y()),
                math.hypot(self._click_pos.x(), self.height() - self._click_pos.y()),
                math.hypot(self.width() - self._click_pos.x(), self.height() - self._click_pos.y())
            )
            self._animation.stop()
            self._animation.setStartValue(0)
            self._animation.setEndValue(self._max_radius)
            self._animation.start()
        super().mousePressEvent(event)
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._radius > 0:
            painter = QPainter()
            if not painter.begin(self): return
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.width(), self.height(), self._border_radius, self._border_radius)
            painter.setClipPath(path)
            opacity = max(0.0, 1.0 - (self._radius / self._max_radius))
            color = QColor(255, 255, 255, int(120 * opacity))
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self._click_pos, int(self._radius), int(self._radius))
            painter.end()
class ComboDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        if option.state & QStyle.State_Selected:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(COLORS['primary_container']))
            rect = option.rect.adjusted(4, 2, -4, -2)
            painter.drawRoundedRect(rect, 4, 4)
            painter.setPen(QColor(COLORS['on_primary_container']))
        else:
            painter.setPen(QColor(COLORS['on_surface']))
        painter.drawText(option.rect.adjusted(12, 0, 0, 0), Qt.AlignVCenter, index.data())
        painter.restore()
class ComboListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setUniformItemSizes(True)
        self.setStyleSheet("background: transparent; border: none; outline: none;")
    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(COLORS['outline_variant']), 1))
        painter.setBrush(QColor(COLORS['surface_container_low']))
        painter.drawRoundedRect(self.viewport().rect().adjusted(1, 1, -1, -1), 8, 8)
        painter.end()
        super().paintEvent(event)
class MaterialComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        view = ComboListView(self)
        view.setItemDelegate(ComboDelegate(view))
        self.setView(view)
        self.view().window().setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.view().window().setAttribute(Qt.WA_TranslucentBackground, True)
        self.view().window().setStyleSheet("background: transparent;")
    def showPopup(self):
        super().showPopup()
        if self.count() == 0: return
        row_height = self.view().sizeHintForRow(0)
        if row_height <= 0: row_height = 32
        max_visible = min(self.count(), 12)
        target_height = max_visible * row_height + 8
        self.view().window().resize(self.width(), target_height)
        pos = self.mapToGlobal(QPoint(0, self.height()))
        self.view().window().move(pos.x(), pos.y())
