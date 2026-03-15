/**
 * Direct Gemini Live API WebSocket from browser.
 * No server proxy — audio and images go straight to Gemini.
 * Server is only used for REST (Document AI, Sheets, Search).
 */

class LiveWebSocket {
    constructor(apiKey, model) {
        this.apiKey = apiKey;
        this.model = model || "models/gemini-2.5-flash-native-audio-preview-12-2025";
        this.ws = null;
        this.ready = false;

        // Audio decode worker (off main thread)
        this._audioWorker = new Worker(URL.createObjectURL(new Blob([`
            self.onmessage = (e) => {
                const base64 = e.data;
                const binary = atob(base64);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
                self.postMessage(bytes.buffer, [bytes.buffer]);
            };
        `], { type: "application/javascript" })));
        this._audioWorker.onmessage = (e) => {
            if (this.onAudioData) this.onAudioData(new Uint8Array(e.data));
        };

        // Callbacks
        this.onTranscript = null;      // (text) — agent speech text
        this.onUserTranscript = null;  // (text) — user speech text
        this.onAudioData = null;       // (Uint8Array) — agent audio PCM 24kHz
        this.onStatusChange = null;    // (status) — connection state
        this.onToolCall = null;        // (functionCalls) — tool calls from model
        this.onTurnComplete = null;    // () — model finished speaking
    }

    connect(systemInstruction) {
        const url = `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=${this.apiKey}`;

        this._setStatus("connecting");
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            // First message MUST be setup
            this.ws.send(JSON.stringify({
                setup: {
                    model: this.model,
                    generationConfig: {
                        responseModalities: ["AUDIO"],
                        speechConfig: {
                            voiceConfig: {
                                prebuiltVoiceConfig: { voiceName: "Aoede" }
                            },
                            languageCode: "en-US"
                        }
                    },
                    systemInstruction: {
                        parts: [{ text: systemInstruction || "You are a helpful assistant." }]
                    },
                    tools: [{ functionDeclarations: this._getToolDeclarations() }],
                    inputAudioTranscription: {},
                    outputAudioTranscription: {}
                }
            }));
        };

        this.ws.onclose = () => {
            this.ready = false;
            this._setStatus("disconnected");
            console.log("[Gemini] Disconnected");
            // Auto-reconnect after 3s
            setTimeout(() => this.connect(systemInstruction), 3000);
        };

        this.ws.onerror = (err) => {
            console.error("[Gemini] Error:", err);
            this._setStatus("disconnected");
        };

        this.ws.onmessage = async (event) => {
            const text = typeof event.data === "string" ? event.data : await event.data.text();
            const msg = JSON.parse(text);

            if (msg.setupComplete) {
                this.ready = true;
                this._setStatus("connected");
                console.log("[Gemini] Ready");
                return;
            }

            if (msg.serverContent) {
                const sc = msg.serverContent;

                // Audio from model
                if (sc.modelTurn && sc.modelTurn.parts) {
                    for (const part of sc.modelTurn.parts) {
                        if (part.inlineData && this.onAudioData) {
                            this._decodeAudioInWorker(part.inlineData.data);
                        }
                        // Don't use modelTurn.text — use outputTranscription instead
                    }
                }

                // Agent speech transcription (what the agent said)
                if (sc.outputTranscription && sc.outputTranscription.text && this.onTranscript) {
                    this.onTranscript(sc.outputTranscription.text);
                }
                // User speech transcription (what the user said)
                if (sc.inputTranscription && sc.inputTranscription.text && this.onUserTranscript) {
                    this.onUserTranscript(sc.inputTranscription.text);
                }

                // Turn complete
                if (sc.turnComplete && this.onTurnComplete) {
                    this.onTurnComplete();
                }
            }

            if (msg.toolCall && this.onToolCall) {
                this.onToolCall(msg.toolCall.functionCalls);
            }
        };
    }

    sendAudio(int16Array) {
        if (!this.ws || !this.ready) return;
        // Fast base64 encode using chunks to avoid string concat overhead
        const bytes = new Uint8Array(int16Array.buffer, int16Array.byteOffset, int16Array.byteLength);
        const chunkSize = 8192;
        let binary = "";
        for (let i = 0; i < bytes.length; i += chunkSize) {
            binary += String.fromCharCode.apply(null, bytes.subarray(i, Math.min(i + chunkSize, bytes.length)));
        }
        this.ws.send(JSON.stringify({
            realtimeInput: {
                audio: {
                    data: btoa(binary),
                    mimeType: "audio/pcm;rate=16000"
                }
            }
        }));
    }

    sendImage(base64Data, mimeType) {
        if (!this.ws || !this.ready) return;
        this.ws.send(JSON.stringify({
            clientContent: {
                turns: [{
                    role: "user",
                    parts: [{
                        inlineData: {
                            mimeType: mimeType || "image/jpeg",
                            data: base64Data
                        }
                    }, {
                        text: "[System: New invoice photo. Say vendor and total ONLY. One sentence.]"
                    }]
                }],
                turnComplete: true
            }
        }));
    }

    sendText(text) {
        if (!this.ws || !this.ready) return;
        this.ws.send(JSON.stringify({
            clientContent: {
                turns: [{
                    role: "user",
                    parts: [{ text: text }]
                }],
                turnComplete: true
            }
        }));
    }

    sendGrounding(invoiceId, groundingText) {
        if (!this.ws || !this.ready) return;
        this.ws.send(JSON.stringify({
            clientContent: {
                turns: [{
                    role: "user",
                    parts: [{ text: groundingText }]
                }],
                turnComplete: true
            }
        }));
    }

    _decodeAudioInWorker(base64) {
        this._audioWorker.postMessage(base64);
    }

    _setStatus(status) {
        if (this.onStatusChange) this.onStatusChange(status);
    }

    sendToolResponse(functionResponses) {
        if (!this.ws || !this.ready) return;
        this.ws.send(JSON.stringify({
            toolResponse: { functionResponses }
        }));
    }

    _getToolDeclarations() {
        return [
            {
                name: "manage_recipes",
                description: "Manage extraction recipes — custom Gemini Vision prompts that auto-run on future invoice uploads. Actions: create (save new recipe), test (run against invoice to verify), list (show user's subscribed recipes), delete (remove recipe — creator deletes permanently, others just unsubscribe), search (find community recipes by regime/industry), subscribe (add existing recipe to your list), unsubscribe (remove from your list).",
                parameters: {
                    type: "OBJECT",
                    properties: {
                        action: { type: "STRING", description: "One of: create, test, list, delete, search, subscribe, unsubscribe." },
                        name: { type: "STRING", description: "Recipe name in snake_case (for create/test/delete)." },
                        description: { type: "STRING", description: "What this recipe extracts (for create)." },
                        extraction_prompt: { type: "STRING", description: "The Gemini Vision prompt (for create)." },
                        trigger_regime: { type: "STRING", description: "Auto-match tax regime, e.g. JP_CT (for create/search)." },
                        trigger_industry: { type: "STRING", description: "Auto-match industry, e.g. construction (for create/search)." },
                        trigger_keywords: { type: "STRING", description: "Comma-separated trigger keywords (for create)." },
                        invoice_id: { type: "STRING", description: "Invoice to test against (for test)." },
                        recipe_id: { type: "STRING", description: "Recipe ID (for subscribe/unsubscribe/test)." },
                        regime: { type: "STRING", description: "Search by regime (for search)." },
                        industry: { type: "STRING", description: "Search by industry (for search)." }
                    },
                    required: ["action"]
                }
            }
        ];
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
