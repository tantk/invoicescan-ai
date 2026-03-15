"""Screen capture for scanning invoices visible on screen."""

import io
import mss
from PIL import Image
from config import CAPTURE_MAX_DIMENSION, CAPTURE_QUALITY


class ScreenCapture:
    def __init__(self):
        self._sct = mss.mss()

    def capture(self) -> bytes:
        """Capture primary monitor as JPEG bytes."""
        monitor = self._sct.monitors[1]
        screenshot = self._sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img = self._resize_fit(img, CAPTURE_MAX_DIMENSION)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=CAPTURE_QUALITY)
        return buf.getvalue()

    @staticmethod
    def _resize_fit(img, max_dim):
        w, h = img.size
        longest = max(w, h)
        if longest <= max_dim:
            return img
        scale = max_dim / longest
        return img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    def close(self):
        self._sct.close()
