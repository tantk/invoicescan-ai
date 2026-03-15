/**
 * Web Worker — image resize + base64 encoding off the main thread.
 * Receives image blobs, returns resized base64 for Gemini.
 */

self.onmessage = async (e) => {
    const { id, blob, maxDim, quality } = e.data;

    try {
        // Create ImageBitmap (works in workers)
        const bitmap = await createImageBitmap(blob);

        const scale = Math.min(1, maxDim / Math.max(bitmap.width, bitmap.height));
        const w = Math.round(bitmap.width * scale);
        const h = Math.round(bitmap.height * scale);

        // OffscreenCanvas for resize
        const canvas = new OffscreenCanvas(w, h);
        const ctx = canvas.getContext("2d");
        ctx.drawImage(bitmap, 0, 0, w, h);
        bitmap.close();

        // Convert to JPEG blob
        const resizedBlob = await canvas.convertToBlob({
            type: "image/jpeg",
            quality: quality || 0.8,
        });

        // Read as base64
        const buffer = await resizedBlob.arrayBuffer();
        const bytes = new Uint8Array(buffer);
        let binary = "";
        // Process in chunks to avoid stack overflow
        const chunkSize = 8192;
        for (let i = 0; i < bytes.length; i += chunkSize) {
            const chunk = bytes.subarray(i, Math.min(i + chunkSize, bytes.length));
            binary += String.fromCharCode.apply(null, chunk);
        }
        const base64 = btoa(binary);

        self.postMessage({ id, base64, width: w, height: h, size: base64.length });
    } catch (err) {
        self.postMessage({ id, error: err.message });
    }
};
