/**
 * Main app — camera mode (scan + voice) or chat mode (upload + text).
 */

(async function () {
    // Fetch API key from server (never hardcoded)
    let API_KEY = "";
    try {
        const configResp = await fetch("/api/config");
        const config = await configResp.json();
        API_KEY = config.gemini_api_key;
        if (!API_KEY) { document.getElementById("transcript-area").innerHTML = '<div class="message system">Server error: GEMINI_API_KEY not configured.</div>'; return; }
    } catch (e) {
        document.getElementById("transcript-area").innerHTML = '<div class="message system">Failed to load config: ' + e.message + '</div>';
        return;
    }
    const SYSTEM_PROMPT = `You are InvoiceScan AI, a voice-powered invoice scanning assistant.
You handle invoices from ANY country and ANY industry.
IMPORTANT: Always respond in English only.

## Your Tool
You have one tool: manage_recipes — for creating, testing, and managing extraction recipes.

### manage_recipes(action, ...)
- create: Save a new recipe (name, extraction_prompt, description required). Triggers optional: trigger_regime, trigger_industry, trigger_keywords. Auto-subscribed and auto-runs on future uploads.
- test: Test recipe against an invoice (name or recipe_id, invoice_id required).
- list: Show user's subscribed recipes.
- delete: Remove a recipe (creator deletes permanently, others just unsubscribe).
- search: Find community recipes by regime/industry.
- subscribe: Add an existing recipe to your list (recipe_id required, from search results).
- unsubscribe: Remove a recipe from your list without deleting it.

### What runs automatically:
Document AI, tax regime detection, tax math verification, fraud detection, compliance, and matching recipes — all run on upload without you calling any tool.

### When to create a recipe:
User says "extract PO number" or "look for project code" → create a recipe → test it → it auto-runs on future invoices.

## Voice Response Style
- When you see an invoice image, say the vendor name and total amount ONLY. One sentence.
- Only mention duplicates when found. Only flag issues (fraud, tax mismatch).
- If the photo is partial or blurry, ask user to retake.
- Keep responses SHORT — the user can see details in the UI.`;

    // Persistent user ID — stored in browser cookie, sent with all requests
    function getCookie(name) {
        const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return m ? decodeURIComponent(m[1]) : null;
    }
    function setCookie(name, value) {
        document.cookie = name + '=' + encodeURIComponent(value) + '; path=/; max-age=31536000; SameSite=Lax';
    }
    const USER_ID = getCookie("invoicescan_uid") || (() => {
        const id = crypto.randomUUID().slice(0, 8);
        setCookie("invoicescan_uid", id);
        return id;
    })();

    const ws = new LiveWebSocket(API_KEY);
    const scanner = new InvoiceScanner();
    const recorder = new AudioRecorder();
    const player = new AudioPlayer();

    const statusDot = document.getElementById("connection-status");
    const transcriptArea = document.getElementById("transcript-area");
    const micBtn = document.getElementById("mic-btn");
    const cameraToggleBtn = document.getElementById("camera-toggle-btn");
    const cameraView = document.getElementById("camera-view");
    const chatView = document.getElementById("chat-view");
    const textInput = document.getElementById("text-input");
    const sendBtn = document.getElementById("send-btn");
    const dataSection = document.getElementById("data-section");
    const dataDisplay = document.getElementById("data-display");
    const headerTitle = document.getElementById("header-title");
    const headerTotal = document.getElementById("header-total");
    const headerAmount = document.getElementById("header-amount");
    const headerCurrency = document.getElementById("header-currency");
    const totalPanel = document.getElementById("total-panel");
    const panelTotalAmount = document.getElementById("panel-total-amount");
    const panelTotalCurrency = document.getElementById("panel-total-currency");
    const panelTotalCount = document.getElementById("panel-total-count");
    const panelDue = document.getElementById("panel-due");
    const panelDueText = document.getElementById("panel-due-text");
    const baseCurrencySelect = document.getElementById("base-currency");
    const currencySave = document.getElementById("currency-save");

    let currentAgentMessage = null;
    let sessionTotal = 0, sessionCount = 0;
    let baseCurrency = localStorage.getItem("invoicescan_currency") || "AUTO";
    let firstCurrency = null;
    baseCurrencySelect.value = baseCurrency;

    function getDisplayCurrency() { return baseCurrency === "AUTO" ? (firstCurrency || "USD") : baseCurrency; }

    function formatShort(n) {
        if (n >= 1000000) return (n/1000000).toFixed(1) + "M";
        if (n >= 100000) return (n/1000).toFixed(0) + "K";
        if (n >= 10000) return (n/1000).toFixed(1) + "K";
        return n.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
    }

    function updateOverlay() {
        const cur = getDisplayCurrency();
        // Header: short format (max 6 chars for amount)
        if (sessionCount > 0) {
            headerTotal.hidden = false;
            document.querySelector(".app-name").hidden = true;
            headerAmount.textContent = formatShort(sessionTotal);
            headerCurrency.textContent = cur;
        }
        // Panel: full detail
        panelTotalAmount.textContent = sessionTotal.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2}) + " " + cur;
        panelTotalCurrency.textContent = cur;
        panelTotalCount.textContent = sessionCount;
    }

    async function addToSessionTotal(amount, currency) {
        if (!amount || amount <= 0) return;
        const dc = getDisplayCurrency();
        if (currency === dc) sessionTotal += amount;
        else { try { const r = await fetch(`/api/convert?amount=${amount}&from_cur=${currency}&to_cur=${dc}`); if(r.ok) sessionTotal+=(await r.json()).converted_amount; else sessionTotal+=amount; } catch{sessionTotal+=amount;} }
        sessionCount++; updateOverlay();
    }
    updateOverlay();

    // Tap header total → expand panel with details + currency settings
    function openPanel(){totalPanel.classList.add("open")} function closePanel(){totalPanel.classList.remove("open")}
    headerTitle.addEventListener("click", openPanel);
    totalPanel.addEventListener("click",(e)=>{if(e.target===totalPanel)closePanel()});
    currencySave.addEventListener("click",()=>{baseCurrency=baseCurrencySelect.value;localStorage.setItem("invoicescan_currency",baseCurrency);closePanel();sessionTotal=0;sessionCount=0;updateOverlay();addMessage("system",`Currency: ${baseCurrency==="AUTO"?"Auto":baseCurrency}`);});

    // 📷 Camera button: tap = open camera / snap, long press = close camera
    async function openCamera() {
        if (scanner.isCameraOpen) return true;
        const ok = await scanner.openCamera();
        if (ok) {
            cameraView.hidden = false;
            document.documentElement.classList.add("camera-on");
            document.body.classList.add("camera-on");
            cameraToggleBtn.classList.add("active");
        }
        return ok;
    }

    function closeCamera() {
        scanner.closeCamera();
        cameraView.hidden = true;
        document.documentElement.classList.remove("camera-on");
        document.body.classList.remove("camera-on");
        cameraToggleBtn.classList.remove("active");
    }

    // Ensure audio playback works on any user gesture
    function ensureAudio() { player._ensureContext(); }

    // 📷 Camera button: tap = open / snap, long press = close
    let camLongPress = null;
    let camWasLong = false;

    cameraToggleBtn.addEventListener("mousedown", () => {
        camWasLong = false;
        camLongPress = setTimeout(() => { camWasLong = true; closeCamera(); }, 600);
    });
    cameraToggleBtn.addEventListener("mouseup", () => clearTimeout(camLongPress));
    cameraToggleBtn.addEventListener("touchstart", (e) => {
        e.preventDefault();
        camWasLong = false;
        camLongPress = setTimeout(() => { camWasLong = true; closeCamera(); }, 600);
    });
    cameraToggleBtn.addEventListener("touchend", (e) => {
        e.preventDefault();
        clearTimeout(camLongPress);
        if (!camWasLong) cameraToggleBtn.click();
    });

    cameraToggleBtn.addEventListener("click", async () => {
        if (camWasLong) return;
        ensureAudio();
        if (scanner.isCameraOpen) {
            scanner.capture();
            addMessage("system", "Captured!");
        } else {
            await openCamera();
        }
    });

    // 📎 Upload button — file picker
    document.getElementById("upload-btn").addEventListener("click", () => {
        ensureAudio();
        document.getElementById("file-input").click();
    });

    scanner.onCameraToggle = (isOpen) => {
        cameraView.hidden = !isOpen;
        cameraToggleBtn.classList.toggle("active", isOpen);
    };

    // Connection
    ws.onStatusChange = (s) => { statusDot.className = "status-dot " + s; };

    // Agent responses
    let thinkingMsg = null;
    function showThinking() { if (!thinkingMsg) thinkingMsg = addMessage("system", "Agent is thinking..."); }
    function clearThinking() { if (thinkingMsg) { thinkingMsg.remove(); thinkingMsg = null; } }

    ws.onTranscript = (text) => { clearThinking(); if(!currentAgentMessage) currentAgentMessage=addMessage("agent",""); currentAgentMessage.textContent+=text; scrollToBottom(); };
    ws.onUserTranscript = (text) => { addMessage("user", text); scrollToBottom(); };
    ws.onTurnComplete = () => { currentAgentMessage = null; };
    ws.onAudioData = (bytes) => { clearThinking(); player.enqueue(bytes); };

    // Tool call dispatch — Gemini calls tools, we execute via server REST
    ws.onToolCall = async (functionCalls) => {
        const responses = [];
        for (const call of functionCalls) {
            try {
                addMessage("system", `Running ${call.name}...`);
                // Inject user_id into all tool calls
                const args = { ...(call.args || {}), user_id: USER_ID };
                const res = await fetch(`/api/tool/${call.name}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(args),
                });
                const result = await res.json();
                responses.push({ id: call.id, name: call.name, response: result });
            } catch (err) {
                responses.push({ id: call.id, name: call.name, response: { error: err.message } });
            }
        }
        ws.sendToolResponse(responses);
    };

    // Status messages (reconnecting, etc.) — shown temporarily
    let statusMsg = null;
    ws.onStatus = (text) => {
        if (statusMsg) statusMsg.remove();
        statusMsg = addMessage("system", text);
        // Auto-remove after 5s
        setTimeout(() => { if (statusMsg) { statusMsg.remove(); statusMsg = null; } }, 5000);
    };

    // ── Thumbnail Queue: pending (left) → done (right) ──────────────
    const thumbStrip = document.getElementById("thumb-strip");
    const thumbPending = document.getElementById("thumb-pending");
    const thumbDone = document.getElementById("thumb-done");
    const thumbDivider = document.getElementById("thumb-divider");
    const imageViewer = document.getElementById("image-viewer");
    const viewerImg = document.getElementById("viewer-img");
    const viewerClose = document.getElementById("viewer-close");
    const thumbDataUrls = {};
    const thumbInvoiceIds = {}; // thumbId → invoiceId
    function updateDivider() {
        thumbDivider.hidden = !(thumbPending.children.length > 0 && thumbDone.children.length > 0);
    }

    function setupThumbEvents(el, thumbId) {
        el.addEventListener("touchstart", (e) => { e.preventDefault(); });
        el.addEventListener("touchend", (e) => { e.preventDefault(); onThumbTap(thumbId); });
        el.addEventListener("click", () => { onThumbTap(thumbId); });
    }

    function onThumbTap(thumbId) {
        viewerImg.src = thumbDataUrls[thumbId] || "";
        imageViewer.hidden = false;
    }

    scanner.onThumbAdd = (thumbId, dataUrl) => {
        thumbStrip.hidden = false;
        thumbDataUrls[thumbId] = dataUrl;
        const item = document.createElement("div");
        item.className = "thumb-item processing";
        item.id = thumbId;
        item.innerHTML = `<img src="${dataUrl || ''}" alt=""><div class="thumb-spinner"></div>`;
        // Tappable even while processing (to expand/view)
        setupThumbEvents(item, thumbId);
        thumbPending.appendChild(item);
        updateDivider();
    };

    scanner.onThumbDone = (thumbId, invoiceId) => {
        const el = document.getElementById(thumbId);
        if (el) {
            el.classList.remove("processing");
            el.classList.add("done");
            el.querySelector(".thumb-spinner")?.remove();
            thumbInvoiceIds[thumbId] = invoiceId;
            thumbDone.prepend(el);
            updateDivider();
        }
    };

    scanner.onThumbError = (thumbId) => {
        const el = document.getElementById(thumbId);
        if (el) {
            el.classList.remove("processing");
            el.classList.add("error");
            el.querySelector(".thumb-spinner")?.remove();
        }
    };

    function closeViewer() {
        imageViewer.hidden = true;
        viewerImg.style.transform = "";
        viewerZoomScale = 1;
    }
    viewerClose.addEventListener("click", closeViewer);
    // Tap outside image to close
    imageViewer.addEventListener("click", (e) => {
        if (e.target === imageViewer || e.target === document.getElementById("viewer-zoom")) closeViewer();
    });

    // Pinch-to-zoom on expanded image
    let viewerZoomScale = 1;
    let initialPinchDist = 0;
    let initialScale = 1;

    viewerImg.addEventListener("touchstart", (e) => {
        if (e.touches.length === 2) {
            e.preventDefault();
            initialPinchDist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            initialScale = viewerZoomScale;
        }
    }, { passive: false });

    viewerImg.addEventListener("touchmove", (e) => {
        if (e.touches.length === 2) {
            e.preventDefault();
            const dist = Math.hypot(
                e.touches[0].clientX - e.touches[1].clientX,
                e.touches[0].clientY - e.touches[1].clientY
            );
            viewerZoomScale = Math.min(5, Math.max(1, initialScale * (dist / initialPinchDist)));
            viewerImg.style.transform = `scale(${viewerZoomScale})`;
        }
    }, { passive: false });

    // Double-tap to reset zoom
    let lastTapTime = 0;
    viewerImg.addEventListener("click", () => {
        const now = Date.now();
        if (now - lastTapTime < 300) {
            viewerZoomScale = 1;
            viewerImg.style.transform = "";
        }
        lastTapTime = now;
    });

    // Invoice image sent directly to Gemini Live (no server proxy)
    scanner.onInvoiceReady = (id, base64, mime) => {
        ws.sendImage(base64, mime);
        addMessage("system", "Photo sent to agent...");
        currentAgentMessage = null;
    };

    // Grounding from Document AI — only send to Gemini if there are flags
    scanner.onGroundingReady = (id, result) => {
        // Check for flags
        const flags = [];
        if (result.is_duplicate) flags.push("DUPLICATE");
        const fraud = result.fraud_check || {};
        if (fraud.risk_level === "CRITICAL" || fraud.risk_level === "HIGH") {
            flags.push("Fraud " + fraud.risk_level + ": " + (result.fraud_warning || []).join("; "));
        }
        if (flags.length > 0) {
            ws.sendText("[System: ALERT for invoice " + id + ": " + flags.join(" | ") + ". Tell user in one sentence.]");
        }
    };

    scanner.onDocAIData = (id, fields, lineItems, result) => {
        if (!fields) return;
        addMessage("system", `Extracted ${Object.keys(fields).length} fields, ${lineItems} line items.`);
        showExtractedData(fields);

        if (result&&result.total_amount_raw) {
            const cur=result.total_currency||result.detected_currency||"USD";
            if(baseCurrency==="AUTO"&&!firstCurrency) firstCurrency=cur;
            addToSessionTotal(result.total_amount_raw, cur);
        }
        if (result&&result.extracted_fields&&result.extracted_fields.due_date) showDueDate(result.extracted_fields.due_date);
        if (result&&result.fraud_check&&(result.fraud_check.risk_level==="CRITICAL"||result.fraud_check.risk_level==="HIGH"))
            addMessage("system",`FRAUD ALERT (${result.fraud_check.risk_level}): ${(result.fraud_warning||[]).join(" ")}`);
        if (result&&result.is_duplicate) addMessage("system","DUPLICATE — not added to Google Sheet.");

        // Camera stays open if toggle is on — user controls it
    };

    scanner.onSheetAdded = () => { addMessage("system","Added to Google Sheet."); };

    // Mic toggle — tap to start/stop continuous streaming
    // Gemini Live API has built-in VAD (voice activity detection),
    // so we just stream audio continuously and it handles turn-taking.
    let isMicOn = false;
    async function toggleMic() {
        if (isMicOn) {
            // Stop
            isMicOn = false;
            micBtn.classList.remove("recording");
            recorder.stop();
            addMessage("system", "Mic off.");
            return;
        }
        // Start
        isMicOn = true;
        micBtn.classList.add("recording");
        currentAgentMessage = null;
        player.stop();
        player._ensureContext(); // Create AudioContext on user gesture
        recorder.onAudioData = (d) => {
            ws.sendAudio(d);
            // Show mic level — check if audio is actually captured
            let sum = 0;
            for (let i = 0; i < d.length; i++) sum += Math.abs(d[i]);
            const avg = sum / d.length;
            if (avg > 500) micBtn.style.boxShadow = "0 0 20px rgba(239,68,68,0.8)";
            else if (avg > 100) micBtn.style.boxShadow = "0 0 10px rgba(239,68,68,0.4)";
            else micBtn.style.boxShadow = "";
        };
        try {
            await recorder.start();
            addMessage("system", "Mic on — speak naturally.");
        } catch (err) {
            console.error("Mic error:", err);
            addMessage("system", "Mic error: " + err.message);
            isMicOn = false;
            micBtn.classList.remove("recording");
        }
    }
    micBtn.addEventListener("click", (e) => { e.preventDefault(); toggleMic(); });

    // Text input
    sendBtn.addEventListener("click",()=>{const t=textInput.value.trim();if(!t)return;addMessage("user",t);ws.sendText(t);textInput.value="";currentAgentMessage=null;showThinking();});
    textInput.addEventListener("keydown",(e)=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();sendBtn.click();}});


    // Helpers
    function addMessage(role,text){const d=document.createElement("div");d.className="message "+role;d.textContent=text;transcriptArea.appendChild(d);scrollToBottom();return d;}
    function scrollToBottom(){transcriptArea.scrollTop=transcriptArea.scrollHeight;}

    function showExtractedData(data){
        dataSection.hidden=false;dataDisplay.innerHTML="";
        const labels={supplier_name:"Vendor",invoice_id:"Invoice #",invoice_date:"Date",due_date:"Due Date",net_amount:"Subtotal",total_tax_amount:"Tax",total_amount:"Total",currency:"Currency",payment_terms:"Terms",supplier_tax_id:"Tax ID"};
        for(const[k,v]of Object.entries(data)){if(!v)continue;const f=document.createElement("div");f.className="data-field";const l=labels[k]||k.replace(/_/g," ").replace(/\b\w/g,c=>c.toUpperCase());const isAmt=["net_amount","total_tax_amount","total_amount"].includes(k);f.innerHTML=`<span class="label">${l}</span><span class="value ${isAmt?"amount":""}">${v}</span>`;dataDisplay.appendChild(f);}
    }

    function showDueDate(s){const d=new Date(s);if(isNaN(d.getTime()))return;const t=new Date();t.setHours(0,0,0,0);d.setHours(0,0,0,0);const diff=Math.round((d-t)/86400000);panelDue.hidden=false;if(diff<0)panelDueText.textContent=`OVERDUE ${Math.abs(diff)} days`;else if(diff<=7)panelDueText.textContent=`${diff} days (soon)`;else panelDueText.textContent=`${diff} days`;}

    ws.connect(SYSTEM_PROMPT);
})();
