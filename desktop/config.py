"""Desktop client configuration for InvoiceScan AI."""

import uuid

# Server connection
SERVER_WS_URL = "ws://localhost:8002/ws"
SERVER_HTTP_URL = "http://localhost:8002"

# User/session
USER_ID = "desktop_user_1"
SESSION_ID = str(uuid.uuid4())

# Screen capture
CAPTURE_MAX_DIMENSION = 1920
CAPTURE_QUALITY = 85  # Higher quality for invoice text readability

# Audio
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK_SIZE = 4096
PLAYBACK_SAMPLE_RATE = 24000
PLAYBACK_CHANNELS = 1

# Hotkeys
PTT_HOTKEY = "F2"       # Hold to talk
SCAN_HOTKEY = "F3"      # Scan invoice on screen

# Overlay
OVERLAY_WIDTH = 380
OVERLAY_HEIGHT = 300
OVERLAY_OPACITY = 0.9
