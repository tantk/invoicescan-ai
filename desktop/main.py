"""InvoiceScan AI Desktop — Transparent Viewfinder.

A transparent overlay window that acts like a camera pointed at your screen.
Position it over an invoice (in email, PDF viewer, browser, etc.) and press F3
to capture and scan. The agent sees exactly what's behind the window.

F2 (hold) = Talk to agent
F3        = Capture what's behind the viewfinder
ESC / X   = Quit
"""

import asyncio
import io
import logging
import sys
import threading

import mss
import numpy as np
import requests
import sounddevice as sd
from collections import deque
from PIL import Image

from PyQt6.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QAction, QCursor
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMenu, QVBoxLayout, QWidget,
    QSizeGrip,
)

from ws_client import InvoiceScanClient
from config import SERVER_HTTP_URL, AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_CHUNK_SIZE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("invoicescan")


class ViewfinderWindow(QWidget):
    """Transparent window with a camera-like frame border.

    The center is fully transparent — you see your desktop/invoice through it.
    The border shows status, controls, and scan results.
    """

    transcript_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    total_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._drag_pos = None
        self._resizing = False
        self._setup_window()
        self._setup_ui()
        self._connect_signals()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(400, 300)
        self.resize(700, 500)

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - 700) // 2,
            (screen.height() - 500) // 2,
        )

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar
        self._top_bar = QWidget()
        self._top_bar.setFixedHeight(36)
        self._top_bar.setStyleSheet("background-color: rgba(15, 23, 42, 220); border-top-left-radius: 8px; border-top-right-radius: 8px;")
        top_layout = QHBoxLayout(self._top_bar)
        top_layout.setContentsMargins(12, 4, 12, 4)

        # Status LED
        self._status_dot = QLabel("●")
        self._status_dot.setFont(QFont("Segoe UI", 10))
        self._status_dot.setStyleSheet("color: #22C55E;")
        top_layout.addWidget(self._status_dot)

        title = QLabel("InvoiceScan AI")
        title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #3B82F6;")
        top_layout.addWidget(title)

        self._status_label = QLabel("Ready")
        self._status_label.setFont(QFont("Segoe UI", 9))
        self._status_label.setStyleSheet("color: #94A3B8;")
        top_layout.addWidget(self._status_label)

        top_layout.addStretch()

        # Scan button (clickable)
        self._scan_btn = QLabel("[ Scan ]")
        self._scan_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._scan_btn.setStyleSheet("color: #3B82F6; padding: 2px 8px;")
        self._scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._scan_btn.mousePressEvent = lambda _: (self.key_press_handler(type('E', (), {'key': lambda: Qt.Key.Key_F3})()) if hasattr(self, 'key_press_handler') else None)
        top_layout.addWidget(self._scan_btn)

        hotkeys = QLabel("F2:Talk  F3:Scan")
        hotkeys.setFont(QFont("Segoe UI", 8))
        hotkeys.setStyleSheet("color: #64748B;")
        top_layout.addWidget(hotkeys)

        close_btn = QLabel("✕")
        close_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        close_btn.setStyleSheet("color: #64748B;")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.mousePressEvent = lambda _: QApplication.quit()
        top_layout.addWidget(close_btn)

        layout.addWidget(self._top_bar)

        # Transparent center (this is where you see through)
        layout.addStretch()

        # Bottom bar
        self._bottom_bar = QWidget()
        self._bottom_bar.setFixedHeight(48)
        self._bottom_bar.setStyleSheet("background-color: rgba(15, 23, 42, 220); border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;")
        bottom_layout = QHBoxLayout(self._bottom_bar)
        bottom_layout.setContentsMargins(12, 4, 12, 4)

        self._transcript_label = QLabel("Position over an invoice and press F3 to scan")
        self._transcript_label.setFont(QFont("Segoe UI", 9))
        self._transcript_label.setStyleSheet("color: #E2E8F0;")
        self._transcript_label.setWordWrap(True)
        bottom_layout.addWidget(self._transcript_label, stretch=1)

        self._total_label = QLabel("0.00 USD")
        self._total_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._total_label.setStyleSheet("color: #10B981;")
        bottom_layout.addWidget(self._total_label)

        layout.addWidget(self._bottom_bar)

    def _connect_signals(self):
        self.transcript_signal.connect(self._on_transcript)
        self.status_signal.connect(self._on_status)
        self.total_signal.connect(self._on_total)

    def paintEvent(self, event):
        """Draw the viewfinder frame — transparent center with border."""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Viewfinder border (the scanning frame)
        border_rect = QRect(0, 36, self.width(), self.height() - 36 - 48)
        pen = QPen(QColor("#3B82F6"), 2)
        pen.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen)
        p.drawRect(border_rect)

        # Corner markers (like a camera viewfinder)
        corner_pen = QPen(QColor("#3B82F6"), 3)
        p.setPen(corner_pen)
        L = 20  # corner length
        x1, y1 = 0, 36
        x2, y2 = self.width() - 1, self.height() - 48

        # Top-left
        p.drawLine(x1, y1, x1 + L, y1)
        p.drawLine(x1, y1, x1, y1 + L)
        # Top-right
        p.drawLine(x2, y1, x2 - L, y1)
        p.drawLine(x2, y1, x2, y1 + L)
        # Bottom-left
        p.drawLine(x1, y2, x1 + L, y2)
        p.drawLine(x1, y2, x1, y2 - L)
        # Bottom-right
        p.drawLine(x2, y2, x2 - L, y2)
        p.drawLine(x2, y2, x2, y2 - L)

        # Resize grip indicator (bottom-right)
        grip_pen = QPen(QColor("#64748B"), 1)
        p.setPen(grip_pen)
        for i in range(3):
            offset = 6 + i * 4
            p.drawLine(self.width() - offset, self.height(),
                       self.width(), self.height() - offset)

        p.end()

    def get_capture_rect(self) -> tuple:
        """Get the screen coordinates of the viewfinder's transparent area."""
        # The transparent area is between top bar and bottom bar
        global_pos = self.mapToGlobal(QPoint(1, 37))
        w = self.width() - 2
        h = self.height() - 37 - 49
        return (global_pos.x(), global_pos.y(), w, h)

    # Dragging (top bar only)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            if pos.y() <= 36:  # Top bar
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            elif pos.x() > self.width() - 20 and pos.y() > self.height() - 20:
                self._resizing = True
                self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos and not self._resizing:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        elif self._resizing:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._drag_pos = event.globalPosition().toPoint()
            new_size = QSize(
                max(self.minimumWidth(), self.width() + delta.x()),
                max(self.minimumHeight(), self.height() + delta.y()),
            )
            self.resize(new_size)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._resizing = False

    # Key events — forwarded to the app
    def keyPressEvent(self, event):
        if hasattr(self, 'key_press_handler'):
            self.key_press_handler(event)

    def keyReleaseEvent(self, event):
        if hasattr(self, 'key_release_handler'):
            self.key_release_handler(event)

    # Right-click menu
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background: #1e293b; color: white; } QMenu::item:selected { background: #3b82f6; }")
        menu.addAction("Quit").triggered.connect(QApplication.quit)
        menu.exec(event.globalPos())

    # Slots
    @pyqtSlot(str)
    def _on_transcript(self, text):
        if text.startswith("\x00"):
            self._transcript_label.setText(text[1:])
        else:
            current = self._transcript_label.text()
            self._transcript_label.setText((current + text)[-200:])

    @pyqtSlot(str)
    def _on_status(self, status):
        colors = {
            "disconnected": "#888", "connecting": "#FFA500",
            "connected": "#22C55E", "listening": "#3B82F6",
            "thinking": "#EAB308", "speaking": "#8B5CF6",
            "scanning": "#EF4444",
        }
        self._status_dot.setStyleSheet(f"color: {colors.get(status, '#888')};")
        labels = {
            "disconnected": "Disconnected", "connecting": "Connecting...",
            "connected": "Ready", "listening": "Listening...",
            "thinking": "Analyzing...", "speaking": "Speaking...",
            "scanning": "Scanning...",
        }
        self._status_label.setText(labels.get(status, status))

    @pyqtSlot(str)
    def _on_total(self, text):
        self._total_label.setText(text)

    # Public API
    def set_transcript(self, text): self.transcript_signal.emit("\x00" + text)
    def append_transcript(self, text): self.transcript_signal.emit(text)
    def set_status(self, status): self.status_signal.emit(status)
    def set_total(self, text): self.total_signal.emit(text)


class InvoiceScanDesktop:
    def __init__(self):
        self._qt_app = QApplication(sys.argv)
        self._window = ViewfinderWindow()
        self._sct = mss.mss()

        # WebSocket
        self._ws = InvoiceScanClient(
            on_audio=self._on_audio,
            on_transcript=self._on_transcript,
            on_status=self._on_status,
        )

        # Audio
        self._recording = False
        self._rec_stream = None
        self._play_stream = None
        self._play_buffer = deque()
        self._play_lock = threading.Lock()

        # Async
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=lambda: (asyncio.set_event_loop(self._loop), self._loop.run_forever()), daemon=True)

        # State
        self._scan_lock = False
        self._session_total = 0.0
        self._session_count = 0

    def run(self):
        self._thread.start()
        asyncio.run_coroutine_threadsafe(self._ws.connect(), self._loop)

        # Start audio playback
        self._play_stream = sd.OutputStream(samplerate=24000, channels=1, dtype="int16", blocksize=4096)
        self._play_stream.start()
        threading.Thread(target=self._play_loop, daemon=True).start()

        # Use Qt key events instead of keyboard library (no admin needed)
        self._window.key_press_handler = self._key_press
        self._window.key_release_handler = self._key_release

        self._window.show()
        logger.info("Viewfinder ready. F2=Talk, F3=Scan, ESC=Quit")

        try:
            self._qt_app.exec()
        finally:
            self._cleanup()

    # ── Key handling ────────────────────────────────────────────────

    def _key_press(self, event):
        key = event.key()
        if key == Qt.Key.Key_F2:
            self._f2_press()
        elif key == Qt.Key.Key_F3:
            self._f3_press()
        elif key == Qt.Key.Key_Escape:
            self._qt_app.quit()

    def _key_release(self, event):
        if event.key() == Qt.Key.Key_F2:
            self._f2_release()

    # ── F2: Push-to-talk ──────────────────────────────────────────────

    def _f2_press(self):
        if self._recording:
            return
        self._recording = True
        self._window.set_status("listening")
        self._window.set_transcript("Listening...")
        self._rec_stream = sd.InputStream(
            samplerate=16000, channels=1, dtype="int16",
            blocksize=4096, callback=self._audio_callback,
        )
        self._rec_stream.start()

    def _f2_release(self):
        if not self._recording:
            return
        self._recording = False
        self._window.set_status("thinking")
        if self._rec_stream:
            self._rec_stream.stop()
            self._rec_stream.close()
            self._rec_stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        if self._recording and self._ws.connected:
            asyncio.run_coroutine_threadsafe(
                self._ws.send_audio(indata.tobytes()), self._loop
            )

    # ── F3: Scan viewfinder area ──────────────────────────────────────

    def _f3_press(self):
        if self._scan_lock:
            return
        self._scan_lock = True
        self._window.set_status("scanning")
        self._window.set_transcript("Capturing...")

        try:
            # Get the viewfinder's transparent area coordinates
            x, y, w, h = self._window.get_capture_rect()

            # Hide window briefly to capture clean screenshot
            self._window.hide()
            QApplication.processEvents()

            # Capture that screen region
            monitor = {"left": x, "top": y, "width": w, "height": h}
            screenshot = self._sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

            # Show window again
            self._window.show()
            QApplication.processEvents()

            # Convert to JPEG
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=90)
            jpeg_bytes = buf.getvalue()

            logger.info(f"Captured {w}x{h} region ({len(jpeg_bytes)} bytes)")
            self._window.set_transcript(f"Captured {w}x{h}. Analyzing...")

            # Send to agent (visual analysis)
            asyncio.run_coroutine_threadsafe(
                self._ws.send_screenshot(jpeg_bytes), self._loop
            )

            # Upload to server (Document AI) in background
            threading.Thread(target=self._upload, args=(jpeg_bytes,), daemon=True).start()

        except Exception as e:
            logger.error(f"Scan error: {e}")
            self._window.set_transcript(f"Scan failed: {e}")
            self._window.show()
        finally:
            self._scan_lock = False

    def _upload(self, jpeg_bytes):
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"desktop_scan_{timestamp}.jpg"
            resp = requests.post(
                f"{SERVER_HTTP_URL}/api/upload",
                files={"file": (filename, io.BytesIO(jpeg_bytes), "image/jpeg")},
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("docai_processed"):
                    # Check duplicate FIRST
                    if data.get("is_duplicate"):
                        warnings = data.get("fraud_warning", ["Already scanned"])
                        self._window.set_transcript(f"DUPLICATE — {warnings[0]}")
                        self._window.set_status("connected")
                        return  # Don't add to session total

                    fields = data.get("extracted_fields", {})
                    vendor = fields.get("supplier_name", "Unknown")
                    total = fields.get("total_amount", "?")
                    currency = data.get("detected_currency", "USD")
                    self._window.set_transcript(f"{vendor} — {total} {currency}")

                    if data.get("sheet_added"):
                        self._window.append_transcript(" | Saved to Sheet")

                    raw = data.get("total_amount_raw")
                    if raw:
                        self._session_total += raw
                        self._session_count += 1
                        self._window.set_total(f"{self._session_total:,.2f} {currency}")

                    fraud = data.get("fraud_check", {})
                    if fraud.get("risk_level") in ("HIGH",):
                        self._window.append_transcript(f" | WARNING: {fraud['risk_level']}")
                else:
                    self._window.set_transcript("No invoice detected in the captured area.")
                self._window.set_status("connected")
        except Exception as e:
            logger.error(f"Upload error: {e}")
            self._window.set_transcript(f"Upload failed: {e}")

    # ── Audio playback ────────────────────────────────────────────────

    def _on_audio(self, audio_bytes):
        self._window.set_status("speaking")
        with self._play_lock:
            self._play_buffer.append(audio_bytes)

    def _play_loop(self):
        import time
        while True:
            chunk = None
            with self._play_lock:
                if self._play_buffer:
                    chunk = self._play_buffer.popleft()
            if chunk:
                arr = np.frombuffer(chunk, dtype=np.int16).reshape(-1, 1)
                self._play_stream.write(arr)
            else:
                time.sleep(0.01)

    def _on_transcript(self, text):
        self._window.append_transcript(text)

    def _on_status(self, status):
        self._window.set_status(status)

    # ── Cleanup ───────────────────────────────────────────────────────

    def _cleanup(self):
        if self._rec_stream:
            self._rec_stream.close()
        if self._play_stream:
            self._play_stream.close()
        self._sct.close()
        asyncio.run_coroutine_threadsafe(self._ws.disconnect(), self._loop)
        self._loop.call_soon_threadsafe(self._loop.stop)


if __name__ == "__main__":
    app = InvoiceScanDesktop()
    app.run()
