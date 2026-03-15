"""Audio I/O — push-to-talk recording + agent voice playback."""

import threading
from collections import deque

import numpy as np
import sounddevice as sd

from config import (
    AUDIO_CHANNELS, AUDIO_CHUNK_SIZE, AUDIO_SAMPLE_RATE,
    PLAYBACK_CHANNELS, PLAYBACK_SAMPLE_RATE,
)


class AudioRecorder:
    def __init__(self, on_audio_chunk=None):
        self._stream = None
        self._recording = False
        self._on_chunk = on_audio_chunk

    def start_recording(self):
        if self._recording:
            return
        self._recording = True
        self._stream = sd.InputStream(
            samplerate=AUDIO_SAMPLE_RATE, channels=AUDIO_CHANNELS,
            dtype="int16", blocksize=AUDIO_CHUNK_SIZE,
            callback=self._callback,
        )
        self._stream.start()

    def stop_recording(self):
        self._recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _callback(self, indata, frames, time_info, status):
        if self._recording and self._on_chunk:
            self._on_chunk(indata.tobytes())

    def close(self):
        self.stop_recording()


class AudioPlayer:
    def __init__(self):
        self._stream = None
        self._buffer = deque()
        self._lock = threading.Lock()
        self._playing = False
        self._thread = None

    def start(self):
        if self._playing:
            return
        self._playing = True
        self._stream = sd.OutputStream(
            samplerate=PLAYBACK_SAMPLE_RATE, channels=PLAYBACK_CHANNELS,
            dtype="int16", blocksize=AUDIO_CHUNK_SIZE,
        )
        self._stream.start()
        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()

    def feed(self, audio_bytes):
        with self._lock:
            self._buffer.append(audio_bytes)

    def _play_loop(self):
        import time
        while self._playing:
            chunk = None
            with self._lock:
                if self._buffer:
                    chunk = self._buffer.popleft()
            if chunk:
                arr = np.frombuffer(chunk, dtype=np.int16).reshape(-1, PLAYBACK_CHANNELS)
                self._stream.write(arr)
            else:
                time.sleep(0.01)

    def close(self):
        self._playing = False
        if self._thread:
            self._thread.join(timeout=1)
        if self._stream:
            self._stream.stop()
            self._stream.close()
