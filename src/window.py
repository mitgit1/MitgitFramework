from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QLabel, QPushButton)
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QCursor

from .theme import COLORS, RADIUS


class TitleBar(QWidget):
    def __init__(self, window, title="App"):
        super().__init__()
        self.window = window
        self._drag_pos = None
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            background-color: {COLORS['surface_container']};
            border-top-left-radius: {RADIUS['medium']}px;
            border-top-right-radius: {RADIUS['medium']}px;
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 5, 0)
        layout.setSpacing(5)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            f"color: {COLORS['on_surface']}; font-size: 13px; "
            f"font-weight: 500; background: transparent;"
        )
        layout.addWidget(self.title_label)
        layout.addStretch()
        
        btn_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLORS['on_surface']};
                font-size: 14px;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: {COLORS['surface_container_high']}; }}
        """
        btn_close_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLORS['on_surface']};
                font-size: 14px;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: #C42B1C; color: white; }}
        """
        
        self.btn_min = QPushButton("—")
        self.btn_min.setStyleSheet(btn_style)
        self.btn_min.setFixedSize(32, 28)
        self.btn_min.clicked.connect(window.showMinimized)
        
        self.btn_max = QPushButton("□")
        self.btn_max.setStyleSheet(btn_style)
        self.btn_max.setFixedSize(32, 28)
        self.btn_max.clicked.connect(self._toggle_max)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setStyleSheet(btn_close_style)
        self.btn_close.setFixedSize(32, 28)
        self.btn_close.clicked.connect(window.close)
        
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

    def _toggle_max(self):
        if self.window.isMaximized():
            self.window.showNormal()
            self.btn_max.setText("□")
        else:
            self.window.showMaximized()
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            if self.window.isMaximized():
                self.window.showNormal()
                self._drag_pos = QPoint(self.window.width() // 2, 20)
            self.window.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class FramelessWindow(QMainWindow):
    RESIZE_MARGIN = 8

    def __init__(self, title="App", icon=None):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self._resize_edge = None
        self._resize_start = None
        self._resize_geom = None

        central = QWidget()
        central.setStyleSheet(
            f"background-color: {COLORS['surface']}; "
            f"border-radius: {RADIUS['medium']}px;"
        )
        self.setCentralWidget(central)

        self._outer_layout = QVBoxLayout(central)
        self._outer_layout.setContentsMargins(0, 0, 0, 0)
        self._outer_layout.setSpacing(0)

        self.title_bar = TitleBar(self, title)
        self._outer_layout.addWidget(self.title_bar)

        self._content_container = QWidget()
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._outer_layout.addWidget(self._content_container, stretch=1)

        if icon:
            self.setWindowIcon(icon)

    def setCentralWidget(self, widget):
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._content_layout.addWidget(widget)

    def _get_edge(self, pos):
        m = self.RESIZE_MARGIN
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        edge = ""
        if y < m: edge += "t"
        elif y > h - m: edge += "b"
        if x < m: edge += "l"
        elif x > w - m: edge += "r"
        return edge

    def _set_cursor(self, edge):
        cursors = {
            "t": Qt.SizeVerCursor, "b": Qt.SizeVerCursor,
            "l": Qt.SizeHorCursor, "r": Qt.SizeHorCursor,
            "tl": Qt.SizeFDiagCursor, "br": Qt.SizeFDiagCursor,
            "tr": Qt.SizeBDiagCursor, "bl": Qt.SizeBDiagCursor,
        }
        if edge in cursors:
            self.setCursor(cursors[edge])
        else:
            self.unsetCursor()

    def mouseMoveEvent(self, event):
        if not self.isMaximized():
            edge = self._get_edge(event.pos())
            self._set_cursor(edge)
            if self._resize_edge and event.buttons() == Qt.LeftButton:
                self._do_resize(event.globalPos())
                return
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.isMaximized():
            edge = self._get_edge(event.pos())
            if edge:
                self._resize_edge = edge
                self._resize_start = event.globalPos()
                self._resize_geom = QRect(self.geometry())
                return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._resize_edge = None
        self._resize_start = None
        self._resize_geom = None
        super().mouseReleaseEvent(event)

    def _do_resize(self, global_pos):
        if not self._resize_geom:
            return
        delta = global_pos - self._resize_start
        geom = QRect(self._resize_geom)
        if "t" in self._resize_edge: geom.setTop(geom.top() + delta.y())
        if "b" in self._resize_edge: geom.setBottom(geom.bottom() + delta.y())
        if "l" in self._resize_edge: geom.setLeft(geom.left() + delta.x())
        if "r" in self._resize_edge: geom.setRight(geom.right() + delta.x())
        if geom.width() >= 400 and geom.height() >= 300:
            self.setGeometry(geom)