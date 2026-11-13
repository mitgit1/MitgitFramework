import math
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QLabel, QRadioButton, QCheckBox, QDialog, QWidget)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPainterPath, QPen, QFont

try:
    import sip
except ImportError:
    from PyQt5 import sip

from .theme import COLORS, RADIUS
from .widgets import RippleButton, MaterialComboBox

_groups = {}

class Frame(QFrame):
    def __init__(self, parent=None, variant="surface_container", padding=15, layout="vbox", spacing=8, border=False):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True) 
        
        bg_color = COLORS.get(variant, "transparent") if variant != "transparent" else "transparent"
        border_css = f"border: 1px solid {COLORS['outline_variant']};" if border else "border: none;"
        
        if variant != "transparent":
            self.setStyleSheet(f"""
                QFrame {{ background-color: {bg_color}; border-radius: {RADIUS['medium']}px; {border_css} }}
            """)
        else:
            self.setStyleSheet("QFrame { background: transparent; border: none; }")
            
        if layout == "vbox":
            self.layout = QVBoxLayout(self)
        else:
            self.layout = QHBoxLayout(self)
            
        self.layout.setContentsMargins(padding, padding, padding, padding)
        self.layout.setSpacing(spacing)

    def add(self, widget, stretch=0):
        self.layout.addWidget(widget, stretch)
        return widget

    def add_layout(self, layout):
        self.layout.addLayout(layout)

class Button(RippleButton):
    def __init__(self, text="", variant="primary", parent=None, icon=None, border_radius=None):
        rad = border_radius if border_radius is not None else RADIUS['small']
        super().__init__(text, parent, border_radius=rad)
        
        if variant == "primary":
            bg, color, hover = COLORS['primary'], COLORS['on_primary'], COLORS['on_primary_container']
        elif variant == "play":
            bg, color, hover = "#3D891C", "white", "#4CAF50"
        elif variant == "danger":
            bg, color, hover = COLORS['error'], COLORS['on_error'], "#FF8A80"
        elif variant == "surface":
            bg, color, hover = COLORS['surface_container_high'], COLORS['on_surface'], COLORS['surface_container_highest']
        else:
            bg, color, hover = "transparent", COLORS['primary'], COLORS['surface_container_high']

        self.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {bg}; color: {color}; border: none; 
                border-radius: {rad}px; font-weight: 500; padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:disabled {{ background-color: {COLORS['surface_container_highest']}; color: {COLORS['on_surface_variant']}; }}
        """)
        if icon: self.setIcon(icon)

class NavButton(RippleButton):
    def __init__(self, text="", icon=None, parent=None):
        super().__init__("", parent, border_radius=16)
        self.setCheckable(True)
        self.setAutoExclusive(True)
        self._icon = icon
        self._text = text
        self.setFixedSize(90, 75)
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter()
        if not painter.begin(self): return
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        
        if self.isChecked():
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(COLORS['surface_container_high']))
            cap_rect = QRect(center_x - 25, 8, 50, 32)
            painter.drawRoundedRect(cap_rect, 16, 16)
        
        if self._icon:
            icon_size = 24
            icon_rect = QRect(center_x - icon_size // 2, 8 + (32 - icon_size) // 2, icon_size, icon_size)
            self._icon.paint(painter, icon_rect, Qt.AlignCenter)
            
        painter.setPen(QColor(COLORS['on_surface']))
        painter.setFont(QFont("Segoe UI", 9))
        text_rect = QRect(0, 48, self.width(), 20)
        painter.drawText(text_rect, Qt.AlignHCenter | Qt.AlignTop, self._text)
        painter.end()

class Input(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)

class MaterialCheckBox(QCheckBox):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._progress = 0.0
        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutQuad)
        self.toggled.connect(self._animate)
        self.setMinimumHeight(32)
        self.setStyleSheet(f"QCheckBox {{ color: {COLORS['on_surface']}; font-size: 14px; padding-left: 36px; background: transparent; outline: none; }} QCheckBox::indicator {{ width: 0px; height: 0px; }}")
        if self.isChecked(): self._progress = 1.0

    def _animate(self, checked):
        self._animation.stop()
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(1.0 if checked else 0.0)
        self._animation.start()

    @pyqtProperty(float)
    def progress(self): return self._progress

    @progress.setter
    def progress(self, value):
        if self._progress != value:
            self._progress = value
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter()
        if not painter.begin(self): return
        painter.setRenderHint(QPainter.Antialiasing)
        
        cx, cy = 16, self.height() // 2
        left, top, size = cx - 9, cy - 9, 18
        
        if self._progress > 0.01:
            painter.setPen(Qt.NoPen)
            bg_color = QColor(COLORS['primary'])
            bg_color.setAlphaF(self._progress)
            painter.setBrush(bg_color)
            painter.drawRoundedRect(left, top, size, size, 2, 2)
            
        painter.setPen(QPen(QColor(COLORS['outline']), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(left, top, size, size, 2, 2)
        
        if self._progress > 0.01:
            check_color = QColor(COLORS['on_primary']) 
            check_color.setAlphaF(self._progress)
            pen = QPen(check_color, 2)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            path = QPainterPath()
            path.moveTo(cx - 5, cy)
            path.lineTo(cx - 1, cy + 4)
            path.lineTo(cx + 6, cy - 4)
            painter.drawPath(path)
        painter.end()

class Checkbox(MaterialCheckBox):
    def __init__(self, text="", group_id=None, parent=None):
        super().__init__(text, parent)
        self.group_id = group_id
        if group_id:
            if group_id not in _groups:
                _groups[group_id] = []
            _groups[group_id].append(self)
            self.toggled.connect(self._on_toggle)

    def _on_toggle(self, checked):
        if checked and self.group_id:
            for cb in _groups[self.group_id]:
                if cb != self and not sip.isdeleted(cb) and cb.isChecked():
                    cb.setChecked(False)

class ComboBox(MaterialComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)

class MaterialDialog(QDialog):
    def __init__(self, parent, title, text, is_confirm=False):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scrim = QWidget(self)
        self.scrim.setStyleSheet(f"background-color: {COLORS.get('scrim', '#80000000')};")
        main_layout.addWidget(self.scrim)
        
        scrim_layout = QVBoxLayout(self.scrim)
        scrim_layout.setAlignment(Qt.AlignCenter)
        
        self.frame = Frame(variant="surface_container", padding=24)
        self.frame.setFixedWidth(400)
        self.frame.setStyleSheet(f"QFrame {{ background-color: {COLORS['surface_container_high']}; border-radius: {RADIUS.get('extra_large', 28)}px; }}")
        
        f_layout = QVBoxLayout(self.frame)
        f_layout.setSpacing(15)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 20px; font-weight: 500; color: {COLORS['on_surface']}; background: transparent;")
        
        lbl_text = QLabel(text)
        lbl_text.setWordWrap(True)
        lbl_text.setStyleSheet(f"font-size: 14px; color: {COLORS['on_surface_variant']}; background: transparent;")
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        if is_confirm:
            btn_no = Button("No", variant="text")
            btn_no.clicked.connect(self.reject)
            btn_layout.addWidget(btn_no)
            
        btn_ok = Button("OK" if not is_confirm else "Yes", variant="primary")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ok)
        
        f_layout.addWidget(lbl_title)
        f_layout.addWidget(lbl_text)
        f_layout.addSpacing(10)
        f_layout.addLayout(btn_layout)
        
        scrim_layout.addWidget(self.frame)
        
    def showEvent(self, event):
        if self.parent():
            self.resize(self.parent().size())
        super().showEvent(event)