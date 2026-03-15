"""WebSocket client for InvoiceScan AI desktop app."""

import asyncio
import base64
import json
import logging

import websockets

from config import SERVER_WS_URL, USER_ID, SESSION_ID

logger = logging.getLogger(__name__)


class InvoiceScanClient:
    def __init__(self, on_audio=None, on_transcript=None, on_status=None,
                 on_compaction=None):
        self._ws = None
        self._on_audio = on_audio
        self._on_transcript = on_transcript
        self._on_status = on_status
        self._on_compaction = on_compaction
        self._connected = False

    @property
    def connected(self):
        return self._connected

    async def connect(self):
        url = f"{SERVER_WS_URL}/{USER_ID}/{SESSION_ID}"
        logger.info(f"Connecting to {url}")
        self._set_status("connecting")
        try:
            self._ws = await websockets.connect(
                url, max_size=10 * 1024 * 1024, ping_interval=20,
            )
            self._connected = True
            self._set_status("connected")
            asyncio.create_task(self._receive_loop())
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._set_status("disconnected")

    async def _receive_loop(self):
        try:
            async for message in self._ws:
                if isinstance(message, bytes):
                    if self._on_audio:
                        self._on_audio(message)
                elif isinstance(message, str):
                    data = json.loads(message)
                    if data.get("type") == "transcript" and self._on_transcript:
                        self._on_transcript(data["data"])
                    elif data.get("type") == "compaction" and self._on_compaction:
                        self._on_compaction(data["data"])
        except websockets.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Receive error: {e}")
        finally:
            self._connected = False
            self._set_status("disconnected")

    async def send_audio(self, audio_bytes):
        if self._ws and self._connected:
            await self._ws.send(audio_bytes)

    async def send_screenshot(self, jpeg_bytes):
        """Send screenshot as invoice image to the live agent."""
        if self._ws and self._connected:
            payload = json.dumps({
                "type": "live_frame",
                "data": base64.b64encode(jpeg_bytes).decode("utf-8"),
                "mime_type": "image/jpeg",
            })
            await self._ws.send(payload)

    async def send_text(self, text):
        if self._ws and self._connected:
            await self._ws.send(json.dumps({"type": "text", "data": text}))

    async def disconnect(self):
        if self._ws:
            await self._ws.close()
        self._connected = False
        self._set_status("disconnected")

    def _set_status(self, status):
        if self._on_status:
            self._on_status(status)
