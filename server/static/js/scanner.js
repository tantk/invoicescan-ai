/**
 * Invoice scanning — camera viewfinder + snap, or upload from gallery.
 *
 * Two flows:
 *   Tap (snap)        → Opens viewfinder, tap again to capture (Flow B)
 *   Long hold (upload) → File picker, Document AI first (Flow A)
 *
 * No frames are sent to Gemini — viewfinder is for the user only.
 */

class InvoiceScanner {
    constructor() {
        this.currentInvoiceId = null;
        this.onInvoiceReady = null;    // (id, base64, mime)
        this.onGroundingReady = null;  // (id, result)
        this.onDocAIData = null;       // (id, fields, lineItems, result)
        this.onSheetAdded = null;      // (id)
        this.onCameraToggle = null;    // (isOpen: boolean)

        this._stream = null;
        this._cameraOpen = false;
        this._processing = false;

        this.onThumbAdd = null;      // (thumbId, dataUrl) — new thumbnail
        this.onThumbDone = null;     // (thumbId, invoiceId) — processing done
        this.onThumbError = null;    // (thumbId) — processing failed

        this.fileInput = document.getElementById("file-input");
        this.placeholder = document.getElementById("placeholder");
        this.video = document.getElementById("camera-preview");

        this._canvas = document.createElement("canvas");
        this._ctx = this._canvas.getContext("2d");

        // Web Worker for image resize (off main thread)
        this._worker = new Worker("/js/image-worker.js");
        this._workerCallbacks = {};
        this._workerId = 0;
        this._worker.onmessage = (e) => {
            const cb = this._workerCallbacks[e.data.id];
            if (cb) {
                delete this._workerCallbacks[e.data.id];
                if (e.data.error) cb.reject(new Error(e.data.error));
                else cb.resolve(e.data.base64);
            }
        };

        this._setupListeners();
    }

    get isCameraOpen() { return this._cameraOpen; }

    _setupListeners() {
        if (this.fileInput) {
            this.fileInput.addEventListener("change", (e) => {
                if (e.target.files.length > 0) this._handleFile(e.target.files[0], "A");
            });
        }

        const uploadArea = document.getElementById("upload-area");
        if (uploadArea) {
            uploadArea.addEventListener("dragover", (e) => { e.preventDefault(); });
            uploadArea.addEventListener("drop", (e) => {
                e.preventDefault();
                if (e.dataTransfer.files.length > 0) this._handleFile(e.dataTransfer.files[0], "A");
            });
        }
    }

    // ── Camera Viewfinder ─────────────────────────────────────────────

    async openCamera() {
        try {
            const isPortrait = window.innerHeight > window.innerWidth;
            const videoConstraints = isPortrait
                ? { facingMode: "environment", width: { ideal: 1080 }, height: { ideal: 1920 }, aspectRatio: { ideal: 9/16 } }
                : { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } };

            this._stream = await navigator.mediaDevices.getUserMedia({
                video: videoConstraints,
            });
            this.video.srcObject = this._stream;
            this._cameraOpen = true;
            if (this.onCameraToggle) this.onCameraToggle(true);
            return true;
        } catch (err) {
            console.error("Camera error:", err.message);
            return false;
        }
    }

    closeCamera() {
        this._cameraOpen = false;
        if (this._stream) {
            this._stream.getTracks().forEach(t => t.stop());
            this._stream = null;
        }
        if (this.onCameraToggle) this.onCameraToggle(false);
    }

    async capture() {
        if (!this._cameraOpen || !this.video.videoWidth) return;

        this._canvas.width = this.video.videoWidth;
        this._canvas.height = this.video.videoHeight;
        this._ctx.drawImage(this.video, 0, 0);

        this._canvas.toBlob(
            (b) => {
                const file = new File([b], "snap_" + Date.now() + ".jpg", { type: "image/jpeg" });
                this._handleFile(file, "B");
            },
            "image/jpeg", 0.92
        );
    }

    // ── File Processing ──────────────────────────────────────────────

    async _handleFile(file, flow) {
        const allowed = ["image/jpeg", "image/png", "image/webp", "image/gif", "application/pdf"];
        if (!allowed.includes(file.type)) {
            alert("Please upload a JPEG, PNG, or PDF file.");
            return;
        }

        const thumbId = "t_" + Date.now();
        const dataUrl = file.type.startsWith("image/") ? URL.createObjectURL(file) : null;

        if (this.onThumbAdd) this.onThumbAdd(thumbId, dataUrl);
        if (this.placeholder) this.placeholder.style.display = "none";

        // Send original image to Gemini (no resize — accuracy over speed for financial data)
        const geminiBase64 = await new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.readAsDataURL(file);
        });

        try {
            if (flow === "B") {
                // Flow B: send resized image to Gemini immediately
                if (this.onInvoiceReady) this.onInvoiceReady(null, geminiBase64, "image/jpeg");
                // Full-res to server in parallel
                const result = await this._upload(file);
                if (this.onGroundingReady) this.onGroundingReady(result.invoice_id, result);
                this._handleResult(result);
                if (this.onThumbDone) this.onThumbDone(thumbId, result.invoice_id);
            } else {
                // Flow A: server first, then resized image to Gemini
                const result = await this._upload(file);
                if (this.onInvoiceReady) this.onInvoiceReady(result.invoice_id, geminiBase64, "image/jpeg");
                this._handleResult(result);
                if (this.onThumbDone) this.onThumbDone(thumbId, result.invoice_id);
            }
        } catch (err) {
            console.error("Upload error:", err);
            if (this.onThumbError) this.onThumbError(thumbId);
        } finally {
            this.fileInput.value = "";
        }
    }

    async _resizeForGemini(file, maxDim) {
        if (!file.type.startsWith("image/")) {
            // PDF — can't resize, read as-is
            return new Promise(r => {
                const reader = new FileReader();
                reader.onload = () => r(reader.result.split(",")[1]);
                reader.readAsDataURL(file);
            });
        }
        // Resize in Web Worker (off main thread)
        const id = ++this._workerId;
        return new Promise((resolve, reject) => {
            this._workerCallbacks[id] = { resolve, reject };
            this._worker.postMessage({ id, blob: file, maxDim, quality: 0.95 });
        });
    }

    async _upload(file) {
        const m = document.cookie.match(/(?:^|; )invoicescan_uid=([^;]*)/);
        const userId = m ? decodeURIComponent(m[1]) : "default";
        const formData = new FormData();
        formData.append("file", file);
        const response = await fetch(`/api/upload?user_id=${encodeURIComponent(userId)}`, { method: "POST", body: formData });
        if (!response.ok) throw new Error(`Upload failed: ${response.statusText}`);
        return await response.json();
    }

    _handleResult(result) {
        this.currentInvoiceId = result.invoice_id;
        if (result.docai_processed && this.onDocAIData) {
            this.onDocAIData(result.invoice_id, result.extracted_fields, result.line_item_count, result);
        }
        if (result.sheet_added && this.onSheetAdded) {
            this.onSheetAdded(result.invoice_id);
        }
    }
}
