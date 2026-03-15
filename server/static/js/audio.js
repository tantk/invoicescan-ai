/**
 * Audio recording (AudioWorklet) and playback.
 * Mic capture + resampling runs on a dedicated audio thread.
 * Main thread stays free for camera rendering.
 */

class AudioRecorder {
    constructor() {
        this.stream = null;
        this.context = null;
        this.workletNode = null;
        this.recording = false;
        this.onAudioData = null; // callback(Int16Array)
    }

    async start() {
        if (this.recording) return;

        this.stream = await navigator.mediaDevices.getUserMedia({
            audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
        });

        this.context = new AudioContext();
        console.log("[Audio] Native sample rate:", this.context.sampleRate);

        // Load worklet processor (runs on audio thread)
        await this.context.audioWorklet.addModule("/js/audio-worklet.js");

        const source = this.context.createMediaStreamSource(this.stream);
        this.workletNode = new AudioWorkletNode(this.context, "mic-processor");

        // Receive resampled Int16 from audio thread
        this.workletNode.port.onmessage = (e) => {
            if (this.onAudioData) {
                this.onAudioData(new Int16Array(e.data));
            }
        };

        source.connect(this.workletNode);
        // AudioWorklet doesn't need to connect to destination
        this.recording = true;
    }

    stop() {
        this.recording = false;
        if (this.workletNode) {
            this.workletNode.port.postMessage("stop");
            this.workletNode.disconnect();
            this.workletNode = null;
        }
        if (this.context) {
            this.context.close();
            this.context = null;
        }
        if (this.stream) {
            this.stream.getTracks().forEach((t) => t.stop());
            this.stream = null;
        }
    }
}

class AudioPlayer {
    constructor() {
        this.context = null;
        this._pendingSamples = [];
        this._flushTimer = null;
        this._nextStartTime = 0;
    }

    _ensureContext() {
        if (!this.context || this.context.state === "closed") {
            this.context = new AudioContext({ sampleRate: 24000 });
            this._nextStartTime = 0;
        }
        if (this.context.state === "suspended") {
            this.context.resume();
        }
    }

    enqueue(pcmBytes) {
        this._ensureContext();

        // Accumulate chunks, flush in batches (less main thread work)
        const int16 = new Int16Array(pcmBytes.buffer, pcmBytes.byteOffset, pcmBytes.byteLength / 2);
        this._pendingSamples.push(int16);

        if (!this._flushTimer) {
            this._flushTimer = setTimeout(() => this._flush(), 80);
        }
    }

    _flush() {
        this._flushTimer = null;
        if (this._pendingSamples.length === 0) return;

        let totalLen = 0;
        for (const s of this._pendingSamples) totalLen += s.length;
        const merged = new Float32Array(totalLen);
        let offset = 0;
        for (const s of this._pendingSamples) {
            for (let i = 0; i < s.length; i++) merged[offset++] = s[i] / 32768;
        }
        this._pendingSamples = [];

        const buffer = this.context.createBuffer(1, merged.length, 24000);
        buffer.getChannelData(0).set(merged);

        // Gapless scheduling: start exactly when previous buffer ends
        const now = this.context.currentTime;
        const startAt = Math.max(now, this._nextStartTime);

        const source = this.context.createBufferSource();
        source.buffer = buffer;
        source.connect(this.context.destination);
        source.start(startAt);

        this._nextStartTime = startAt + buffer.duration;
    }

    stop() {
        this._pendingSamples = [];
        clearTimeout(this._flushTimer);
        this._flushTimer = null;
        this._nextStartTime = 0;
        if (this.context) {
            this.context.close();
            this.context = null;
        }
    }
}
