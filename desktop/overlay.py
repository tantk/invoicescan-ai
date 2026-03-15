"""InvoiceScan AI desktop overlay — floating always-on-top widget.

Shows: status, transcript, session total, due date, hotkey hints.
"""

from PyQt6.QtCore import Qt, QPoint, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QBrush, QAction
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMenu, QScrollArea, QVBoxLayout, QWidget,
)

from config import OVERLAY_WIDTH, OVERLAY_HEIGHT, OVERLAY_OPACITY


class StatusLED(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._color = QColor("#888888")

    def set_status(self, status):
        colors = {
            "disconnected": "#888888", "connecting": "#FFA500",
            "connected": "#22C55E", "listening": "#3B82F6",
            "thinking": "#EAB308", "speaking": "#8B5CF6",
            "scanning": "#EF4444",
        }
        self._color = QColor(colors.get(status, "#888888"))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(self._color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(1, 1, 10, 10)
        p.end()


class OverlayWidget(QWidget):
    transcript_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    ptt_signal = pyqtSignal(bool)
    total_signal = pyqtSignal(str)  # session total text
    due_signal = pyqtSignal(str, str)  # due text, color

    def __init__(self):
        super().__init__()
        self._drag_pos = QPoint()
        self._setup_window()
        self._setup_ui()
        self._connect_signals()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setFixedSize(OVERLAY_WIDTH, OVERLAY_HEIGHT)
        # Solid dark background — works on all Windows versions
        self.setStyleSheet("OverlayWidget { background-color: #0f172a; border-radius: 12px; }")
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - OVERLAY_WIDTH - 20,
                  screen.height() - OVERLAY_HEIGHT - 60)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Header: LED + title
        header = QHBoxLayout()
        header.setSpacing(8)
        self._led = StatusLED()
        header.addWidget(self._led)

        title = QLabel("InvoiceScan AI")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #3B82F6;")
        header.addWidget(title)
        header.addStretch()

        self._hotkey_label = QLabel("F2:Talk  F3:Scan")
        self._hotkey_label.setFont(QFont("Segoe UI", 8))
        self._hotkey_label.setStyleSheet("color: #6B7280;")
        header.addWidget(self._hotkey_label)

        # Close button
        close_btn = QLabel("✕")
        close_btn.setFont(QFont("Segoe UI", 12))
        close_btn.setStyleSheet("color: #6B7280;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.mousePressEvent = lambda _: QApplication.quit()
        header.addWidget(close_btn)

        layout.addLayout(header)

        # Status text
        self._status_text = QLabel("Disconnected")
        self._status_text.setFont(QFont("Segoe UI", 9))
        self._status_text.setStyleSheet("color: #9CA3AF;")
        layout.addWidget(self._status_text)

        # Session total bar
        total_row = QHBoxLayout()
        total_label = QLabel("SESSION TOTAL")
        total_label.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        total_label.setStyleSheet("color: #6B7280; letter-spacing: 1px;")
        total_row.addWidget(total_label)
        total_row.addStretch()

        self._total_amount = QLabel("0.00 USD")
        self._total_amount.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._total_amount.setStyleSheet("color: #10B981;")
        total_row.addWidget(self._total_amount)
        layout.addLayout(total_row)

        # Due date
        self._due_label = QLabel("")
        self._due_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._due_label.setStyleSheet("color: #10B981; background: rgba(16,185,129,0.15); border-radius: 4px; padding: 2px 8px;")
        self._due_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._due_label.hide()
        layout.addWidget(self._due_label)

        # Transcript
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical { width: 4px; background: transparent; }"
            "QScrollBar::handle:vertical { background: #4B5563; border-radius: 2px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )
        self._transcript = QLabel("")
        self._transcript.setFont(QFont("Segoe UI", 10))
        self._transcript.setStyleSheet("color: #E5E7EB;")
        self._transcript.setWordWrap(True)
        self._transcript.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self._transcript)
        layout.addWidget(scroll, stretch=1)

    def _connect_signals(self):
        self.transcript_signal.connect(self._on_transcript)
        self.status_signal.connect(self._on_status)
        self.ptt_signal.connect(self._on_ptt)
        self.total_signal.connect(self._on_total)
        self.due_signal.connect(self._on_due)

    # Right-click menu
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background: #1e293b; color: white; padding: 4px; } QMenu::item:selected { background: #3b82f6; }")
        quit_action = menu.addAction("Quit InvoiceScan AI")
        quit_action.triggered.connect(QApplication.quit)
        menu.exec(event.globalPos())

    # Dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    # Slots
    @pyqtSlot(str)
    def _on_transcript(self, text):
        if text == "\x00CLEAR":
            self._transcript.setText("")
            return
        current = self._transcript.text()
        updated = (current + text)[-600:]
        self._transcript.setText(updated)

    @pyqtSlot(str)
    def _on_status(self, status):
        self._led.set_status(status)
        labels = {
            "disconnected": "Disconnected", "connecting": "Connecting...",
            "connected": "Ready — F2 to talk, F3 to scan",
            "listening": "Listening...", "thinking": "Analyzing...",
            "speaking": "Speaking...", "scanning": "Scanning invoice...",
        }
        self._status_text.setText(labels.get(status, status))

    @pyqtSlot(bool)
    def _on_ptt(self, active):
        if active:
            self._hotkey_label.setStyleSheet("color: #EF4444; font-weight: bold;")
            self._hotkey_label.setText("Recording...")
        else:
            self._hotkey_label.setStyleSheet("color: #6B7280;")
            self._hotkey_label.setText("F2:Talk  F3:Scan")

    @pyqtSlot(str)
    def _on_total(self, text):
        self._total_amount.setText(text)

    @pyqtSlot(str, str)
    def _on_due(self, text, color):
        self._due_label.setText(text)
        self._due_label.setStyleSheet(f"color: {color}; background: rgba(255,255,255,0.08); border-radius: 4px; padding: 2px 8px;")
        self._due_label.show()

    # Public API (thread-safe)
    def append_transcript(self, text): self.transcript_signal.emit(text)
    def set_status(self, status): self.status_signal.emit(status)
    def set_ptt_active(self, active): self.ptt_signal.emit(active)
    def set_total(self, text): self.total_signal.emit(text)
    def set_due(self, text, color): self.due_signal.emit(text, color)
    def clear_transcript(self): self.transcript_signal.emit("\x00CLEAR")
