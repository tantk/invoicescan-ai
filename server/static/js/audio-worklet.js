/**
 * AudioWorklet processors — run on a dedicated audio thread.
 * This file is loaded by audioContext.audioWorklet.addModule().
 */

// ── Mic Capture Processor ─────────────────────────────────────────────
// Captures mic input, resamples to 16kHz, converts to Int16, posts to main thread.
class MicProcessor extends AudioWorkletProcessor {
    constructor(options) {
        super();
        this.targetRate = 16000;
        this.nativeRate = sampleRate; // global in AudioWorkletGlobalScope
        this.ratio = this.targetRate / this.nativeRate;
        this.active = true;

        // Accumulate samples, post every ~100ms instead of every 2.7ms
        // At 16kHz target, 1600 samples = 100ms
        this.buffer = new Float32Array(1600);
        this.bufferOffset = 0;

        this.port.onmessage = (e) => {
            if (e.data === "stop") this.active = false;
        };
    }

    process(inputs) {
        if (!this.active) return false;
        const input = inputs[0];
        if (!input || !input[0] || input[0].length === 0) return true;

        const float32 = input[0];

        // Resample to 16kHz
        const newLen = Math.round(float32.length * this.ratio);
        for (let i = 0; i < newLen; i++) {
            const srcIdx = i / this.ratio;
            const idx = Math.floor(srcIdx);
            const frac = srcIdx - idx;
            let sample;
            if (idx + 1 < float32.length) {
                sample = float32[idx] * (1 - frac) + float32[idx + 1] * frac;
            } else {
                sample = float32[idx] || 0;
            }

            this.buffer[this.bufferOffset++] = sample;

            // Buffer full — flush
            if (this.bufferOffset >= this.buffer.length) {
                this._flush();
            }
        }

        return true;
    }

    _flush() {
        const int16 = new Int16Array(this.bufferOffset);
        for (let i = 0; i < this.bufferOffset; i++) {
            const s = Math.max(-1, Math.min(1, this.buffer[i]));
            int16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        this.bufferOffset = 0;
        this.port.postMessage(int16.buffer, [int16.buffer]);
    }
}

registerProcessor("mic-processor", MicProcessor);
