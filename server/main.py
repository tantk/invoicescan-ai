"""FastAPI server for InvoiceScan AI.

Serves the web frontend, handles invoice uploads, and bridges
the Gemini Live API for real-time voice conversation about invoices.

Services:
- Document AI: Structured invoice extraction (grounding)
- Vertex AI Search: Semantic search over past invoices (RAG)
- Memory Bank: Persistent user preferences and history
- Sessions: Persistent conversation state (SQLite or Vertex AI)
"""

import asyncio
import base64
import io
import json
import logging
import os
import traceback
import uuid

from PIL import Image

from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from google.adk.runners import Runner
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

load_dotenv()

from invoice_agent import root_agent, create_session_service, create_memory_service
from invoice_agent.agent import _overlay_commands
from invoice_agent.tools.invoice_parser import invoice_store, process_invoice_on_upload
from invoice_agent.tools.search_store import ingest_invoice_to_search, search_invoices
from invoice_agent.tools.sheets import add_invoice_to_sheet, update_analysis_column
from invoice_agent.tools.fraud_detector import check_duplicate
from invoice_agent.tools.smart_extraction import parse_einvoice_xml, check_confidence_and_escalate
from invoice_agent.tools.currency import detect_currency, convert_amount, parse_and_convert
from invoice_agent.tools.tax_engine import detect_invoice_type, verify_tax_math, validate_compliance
from invoice_agent.tools.context_manager import get_tracker, check_and_compact
from invoice_agent.recipe_mcp import manage_recipes, get_user_recipes, run_recipe

logging.basicConfig(level=logging.INFO)
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("google_adk").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(title="InvoiceScan AI")

# ── Services ──────────────────────────────────────────────────────────────

session_service = create_session_service()
memory_service = create_memory_service()

# ADK Runner with memory support
# When memory_service is set, Runner auto-injects the `load_memory` tool
# so the agent can recall past conversations and user preferences.
runner = Runner(
    agent=root_agent,
    app_name="invoice_scanner",
    session_service=session_service,
    memory_service=memory_service,
)

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── REST Endpoints ────────────────────────────────────────────────────────


@app.get("/api/config")
async def get_config():
    """Return client config (API key from env var, never hardcoded)."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return JSONResponse({"error": "GEMINI_API_KEY not set"}, status_code=500)
    return {"gemini_api_key": api_key}


@app.get("/health")
async def health():
    from invoice_agent.config import (
        DOCAI_ENABLED, VERTEX_SEARCH_ENABLED, MEMORY_BACKEND,
        SESSION_BACKEND, SHEETS_ENABLED,
    )
    return {
        "status": "ok",
        "agent": root_agent.name,
        "services": {
            "document_ai": DOCAI_ENABLED,
            "vertex_search": VERTEX_SEARCH_ENABLED,
            "google_sheets": SHEETS_ENABLED,
            "memory_backend": MEMORY_BACKEND,
            "session_backend": SESSION_BACKEND,
        },
    }


# ── Tool Endpoint (for Gemini Live function calling via browser) ──────────


@app.post("/api/tool/manage_recipes")
async def call_manage_recipes(request: Request):
    """Dispatch manage_recipes tool calls from Gemini Live via the browser."""
    body = await request.json()
    try:
        result = manage_recipes(**body)
        if not isinstance(result, dict):
            result = {"result": result}
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"manage_recipes error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/upload")
async def upload_invoice(file: UploadFile = File(...), user_id: str = "default"):
    """Upload an invoice image/PDF, process with Document AI, ingest into search."""
    allowed_types = {
        "image/jpeg", "image/png", "image/webp",
        "image/gif", "application/pdf",
        "text/xml", "application/xml",
    }
    if file.content_type not in allowed_types:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported file type: {file.content_type}"},
        )

    invoice_id = str(uuid.uuid4())[:8]
    image_bytes = await file.read()

    # Save to disk
    ext = file.filename.rsplit(".", 1)[-1] if file.filename else "jpg"
    filepath = os.path.join(UPLOAD_DIR, f"{invoice_id}.{ext}")
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    # Store in memory for tool access
    invoice_store[invoice_id] = {
        "image_bytes": image_bytes,
        "mime_type": file.content_type,
        "filename": file.filename,
        "filepath": filepath,
    }

    logger.info(f"Invoice uploaded: id={invoice_id} file={file.filename} size={len(image_bytes)}")

    # ── Step 0: Check if it's an XML e-invoice (100% accurate, no OCR needed) ──
    xml_parsed = None
    if file.content_type in ("text/xml", "application/xml") or (
        file.filename and file.filename.lower().endswith(".xml")
    ):
        try:
            xml_parsed = parse_einvoice_xml(image_bytes.decode("utf-8"))
            if xml_parsed:
                invoice_store[invoice_id]["extracted_data"] = xml_parsed
                invoice_store[invoice_id]["grounding_text"] = (
                    f"[GROUNDED INVOICE DATA — ID: {invoice_id}]\n"
                    f"Source: {xml_parsed.get('source', 'e-invoice XML')} — 100% accurate structured data.\n"
                    + "\n".join(
                        f"- {k}: {v['value']}" for k, v in xml_parsed.get("fields", {}).items()
                    )
                )
                logger.info(f"Parsed e-invoice XML for {invoice_id}: {len(xml_parsed.get('fields', {}))} fields")
        except Exception as e:
            logger.warning(f"XML parsing failed for {invoice_id}, falling back to Document AI: {e}")

    # ── Step 1: Document AI extraction (skip if XML already parsed) ──
    docai_result = None
    if xml_parsed:
        docai_result = {"extracted_data": xml_parsed}
    else:
        docai_result = process_invoice_on_upload(invoice_id)

    response = {
        "invoice_id": invoice_id,
        "filename": file.filename,
        "size": len(image_bytes),
        "mime_type": file.content_type,
        "docai_processed": docai_result is not None,
        "search_indexed": False,
        "sheet_added": False,
    }

    if docai_result:
        extracted = docai_result["extracted_data"]

        response["extracted_fields"] = {
            k: v["value"] for k, v in extracted.get("fields", {}).items()
        }
        response["line_item_count"] = len(extracted.get("line_items", []))
        response["annotations"] = extracted.get("annotations", [])

        # ── Step 2: Fraud check FIRST (before logging to Sheets) ──
        fraud_result = check_duplicate(invoice_id)
        is_duplicate = (
            isinstance(fraud_result, dict)
            and fraud_result.get("risk_level") in ("CRITICAL",)
        )

        # ── Step 3: Run remaining tasks IN PARALLEL ──
        # Skip Sheets if duplicate. Search + regime always run.

        async def _ingest_search():
            return ingest_invoice_to_search(
                invoice_id=invoice_id,
                extracted_data=extracted,
                filename=file.filename,
            )

        async def _push_sheets():
            if is_duplicate:
                return False  # Don't log duplicates
            return add_invoice_to_sheet(
                invoice_id=invoice_id,
                extracted_data=extracted,
                filename=file.filename,
            )

        async def _detect_regime():
            return detect_invoice_type(invoice_id)

        search_result, sheet_result, regime_result = await asyncio.gather(
            _ingest_search(),
            _push_sheets(),
            _detect_regime(),
            return_exceptions=True,
        )

        response["search_indexed"] = search_result is True
        response["sheet_added"] = sheet_result is True
        response["is_duplicate"] = is_duplicate

        # Store regime detection for the grounding context
        if isinstance(regime_result, dict) and "detected_regime" in regime_result:
            invoice_store[invoice_id]["detected_regime"] = regime_result.get("detected_regime")
            invoice_store[invoice_id]["detected_industry"] = (
                regime_result.get("industry", {}).get("industry_code")
                if isinstance(regime_result.get("industry"), dict)
                else None
            )
            response["detected_regime"] = regime_result.get("detected_regime")
            response["detected_country"] = regime_result.get("country")
            response["detected_industry"] = (
                regime_result.get("industry", {}).get("industry")
                if isinstance(regime_result.get("industry"), dict)
                else None
            )

        # Detect currency and include converted amount
        invoice_currency = detect_currency(extracted.get("fields", {}))
        response["detected_currency"] = invoice_currency
        total_str = extracted.get("fields", {}).get("total_amount", {})
        if isinstance(total_str, dict):
            total_str = total_str.get("value", "")
        total_val = None
        try:
            cleaned = __import__('re').sub(r"[^\d.\-]", "", str(total_str).replace(",", ""))
            total_val = float(cleaned) if cleaned else None
        except ValueError:
            pass
        if total_val is not None:
            response["total_amount_raw"] = total_val
            response["total_currency"] = invoice_currency

        # Fraud check results
        if isinstance(fraud_result, dict) and "risk_level" in fraud_result:
            response["fraud_check"] = {
                "risk_level": fraud_result["risk_level"],
                "flags": fraud_result.get("total_flags", 0),
            }
            if fraud_result["risk_level"] in ("HIGH", "CRITICAL"):
                response["fraud_warning"] = [
                    f["detail"] for f in fraud_result.get("flags", [])
                    if f.get("severity") in ("HIGH", "CRITICAL")
                ]

        # ── Step 5: Background post-processing → Analysis column ──
        if not is_duplicate and sheet_result:
            asyncio.create_task(
                _run_background_analysis(
                    invoice_id, extracted, fraud_result,
                    user_id=user_id,
                    detected_regime=response.get("detected_regime", ""),
                    detected_industry=response.get("detected_industry", ""),
                )
            )

    # Track context usage for compaction
    # (user_id not available in REST — use a default tracker)
    tracker = get_tracker("default")
    tracker.record_grounding(
        invoice_id,
        extracted.get("fields", {}),
        invoice_store.get(invoice_id, {}).get("grounding_text", ""),
    )
    if fraud_result and isinstance(fraud_result, dict):
        for flag in fraud_result.get("flags", []):
            if flag.get("severity") in ("HIGH", "CRITICAL"):
                tracker.record_issue(flag.get("detail", ""))

    return response


async def _run_background_analysis(
    invoice_id: str, extracted: dict, fraud_result: dict,
    user_id: str = "default", detected_regime: str = "", detected_industry: str = "",
):
    """Run post-processing analysis in background and write to Sheets Analysis column.

    Includes: fraud summary, tax verification, confidence check, compliance,
    and auto-running matching user recipes.
    """
    try:
        findings = []

        # 1. Fraud findings (already computed, just format)
        if isinstance(fraud_result, dict) and fraud_result.get("flags"):
            for flag in fraud_result["flags"]:
                sev = flag.get("severity", "INFO")
                detail = flag.get("detail", "")
                if detail:
                    findings.append(f"[{sev}] {detail}")

        # 2. Tax math verification
        try:
            tax_result = verify_tax_math(invoice_id)
            if isinstance(tax_result, dict):
                if tax_result.get("status") == "mismatch":
                    findings.append(f"[TAX] {tax_result.get('message', 'Tax mismatch detected')}")
                elif tax_result.get("status") == "verified":
                    findings.append("[OK] Tax math verified")
        except Exception as e:
            logger.debug(f"Tax verification skipped for {invoice_id}: {e}")

        # 3. Confidence check — flag low-confidence fields
        try:
            confidence_result = check_confidence_and_escalate(invoice_id)
            if isinstance(confidence_result, dict):
                escalated = confidence_result.get("escalated_fields", [])
                disagreements = confidence_result.get("disagreements", [])
                for d in disagreements:
                    findings.append(f"[REVIEW] {d.get('field', '?')}: DocAI={d.get('docai_value', '?')} vs Vision={d.get('vision_value', '?')}")
                if escalated and not disagreements:
                    findings.append(f"[OK] Re-checked {len(escalated)} low-confidence fields — all confirmed")
        except Exception as e:
            logger.debug(f"Confidence check skipped for {invoice_id}: {e}")

        # 4. Compliance validation
        try:
            compliance_result = validate_compliance(invoice_id)
            if isinstance(compliance_result, dict):
                errors = compliance_result.get("errors", [])
                warnings = compliance_result.get("warnings", [])
                for err in errors:
                    findings.append(f"[COMPLIANCE] {err}")
                for warn in warnings:
                    findings.append(f"[WARN] {warn}")
                if not errors and not warnings:
                    findings.append("[OK] Compliance checks passed")
        except Exception as e:
            logger.debug(f"Compliance check skipped for {invoice_id}: {e}")

        # 5. Auto-run matching user recipes from Firestore
        try:
            matching_recipes = get_user_recipes(user_id, detected_regime, detected_industry)
            for recipe in matching_recipes:
                rid = recipe.get("recipe_id", "")
                recipe_name = recipe.get("name", rid)
                try:
                    rr = run_recipe(rid, invoice_id)
                    if rr.get("status") == "success":
                        findings.append(f"[RECIPE] '{recipe_name}' extracted {len(rr.get('result', {}))} fields")
                        logger.info(f"Auto-ran recipe '{recipe_name}' for {invoice_id}")
                    else:
                        findings.append(f"[RECIPE] '{recipe_name}' failed: {rr.get('error', '?')}")
                except Exception as e:
                    logger.debug(f"Recipe '{recipe_name}' failed for {invoice_id}: {e}")
        except Exception as e:
            logger.debug(f"Recipe auto-run skipped for {invoice_id}: {e}")

        # Write to Analysis column
        if findings:
            analysis_text = " | ".join(findings)
            update_analysis_column(invoice_id, analysis_text)
            logger.info(f"Background analysis for {invoice_id}: {len(findings)} findings")

    except Exception as e:
        logger.error(f"Background analysis failed for {invoice_id}: {e}")


@app.get("/api/invoices/{invoice_id}/annotations")
async def get_annotations(invoice_id: str, fields: str = ""):
    """Get bounding box annotations for overlay display.

    Optional 'fields' param: comma-separated field names to filter.
    E.g., ?fields=supplier_name,total_amount,invoice_id
    If empty, returns all annotations.
    """
    if invoice_id not in invoice_store:
        return JSONResponse(status_code=404, content={"error": "Not found"})

    inv = invoice_store[invoice_id]
    annotations = inv.get("extracted_data", {}).get("annotations", [])

    if fields:
        filter_set = set(f.strip() for f in fields.split(","))
        annotations = [a for a in annotations if a["type"] in filter_set]

    return {"invoice_id": invoice_id, "annotations": annotations}


@app.get("/api/context")
async def get_context_stats():
    """Get context window usage statistics."""
    tracker = get_tracker("default")
    return tracker.get_stats()


@app.get("/api/invoices")
async def list_invoices():
    """List all uploaded invoices."""
    return {
        inv_id: {
            "filename": inv.get("filename"),
            "mime_type": inv.get("mime_type"),
            "has_data": "extracted_data" in inv,
        }
        for inv_id, inv in invoice_store.items()
    }


@app.get("/api/invoices/{invoice_id}/image")
async def get_invoice_image(invoice_id: str):
    """Return base64-encoded invoice image for display."""
    if invoice_id not in invoice_store:
        return JSONResponse(status_code=404, content={"error": "Not found"})

    inv = invoice_store[invoice_id]
    b64 = base64.b64encode(inv["image_bytes"]).decode()
    return {"invoice_id": invoice_id, "mime_type": inv["mime_type"], "data": b64}


@app.get("/api/convert")
async def convert_currency(amount: float, from_cur: str, to_cur: str):
    """Convert amount between currencies using live exchange rates."""
    result = convert_amount(amount, from_cur, to_cur)
    if result:
        return result
    return JSONResponse(status_code=400, content={"error": f"Could not convert {from_cur} to {to_cur}"})


@app.get("/api/search")
async def search_past_invoices(q: str, limit: int = 5):
    """Semantic search across all indexed invoices."""
    results = search_invoices(query=q, max_results=limit)
    return {"query": q, "results": results}


# ── WebSocket (Gemini Live) ──────────────────────────────────────────────


@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, session_id: str):
    """Bidirectional WebSocket for voice + image streaming with Gemini Live API."""
    await websocket.accept()
    logger.info(f"Client connected: user={user_id} session={session_id}")

    # Ensure session exists
    session = await session_service.get_session(
        app_name="invoice_scanner", user_id=user_id, session_id=session_id
    )
    if session is None:
        session = await session_service.create_session(
            app_name="invoice_scanner", user_id=user_id, session_id=session_id
        )

    live_queue = LiveRequestQueue()
    tracker = get_tracker(user_id)

    async def upstream():
        """Forward client audio/images/text into the Live API queue."""
        image_queue_count = 0
        try:
            while True:
                msg = await websocket.receive()

                if msg.get("type") == "websocket.disconnect":
                    break

                if "bytes" in msg:
                    # Raw audio bytes (16-bit PCM, 16kHz mono)
                    first_message.set()
                    raw = msg["bytes"]
                    # Log audio level to verify mic is working
                    import struct
                    samples = struct.unpack(f"<{len(raw)//2}h", raw)
                    peak = max(abs(s) for s in samples) if samples else 0
                    if peak > 1000:
                        logger.info(f"Audio chunk: {len(raw)} bytes, peak={peak}")
                    audio_blob = types.Blob(
                        mime_type="audio/pcm;rate=16000", data=raw
                    )
                    live_queue.send_realtime(audio_blob)
                    tracker.record_voice_turn()

                elif "text" in msg:
                    first_message.set()
                    data = json.loads(msg["text"])
                    msg_type = data.get("type")

                    if msg_type == "live_frame":
                        # Camera preview frame — agent checks quality
                        logger.info(f"Live frame received: {len(data['data'])} chars base64")
                        frame_bytes = base64.b64decode(data["data"])
                        frame_blob = types.Blob(mime_type="image/jpeg", data=frame_bytes)
                        live_queue.send_realtime(frame_blob)

                    elif msg_type == "image":
                        raw_bytes = base64.b64decode(data["data"])
                        mime = data.get("mime_type", "image/jpeg")
                        image_queue_count += 1
                        count = image_queue_count

                        # Resize for Gemini Live (max 1024px) — full-res stays on server for Document AI
                        try:
                            img = Image.open(io.BytesIO(raw_bytes))
                            if max(img.size) > 1024:
                                img.thumbnail((1024, 1024), Image.LANCZOS)
                                buf = io.BytesIO()
                                img.save(buf, format="JPEG", quality=85)
                                image_bytes = buf.getvalue()
                                logger.info(f"Image #{count}: {len(raw_bytes)}→{len(image_bytes)} bytes (resized)")
                            else:
                                image_bytes = raw_bytes
                                logger.info(f"Image #{count}: {len(image_bytes)} bytes (no resize needed)")
                        except Exception:
                            image_bytes = raw_bytes
                            logger.info(f"Image #{count}: {len(image_bytes)} bytes (resize failed, using original)")

                        invoice_id = data.get("invoice_id")
                        batch_hint = f" (photo #{count})" if count > 1 else ""

                        if invoice_id:
                            # Flow A: Document AI done, send image + grounding together
                            logger.info(f"Flow A: image + grounding for {invoice_id}")
                            invoice = invoice_store.get(invoice_id, {})
                            grounding = invoice.get("grounding_text", "")

                            context_text = (
                                f"{grounding}\n\n"
                                f"[System: Invoice '{invoice_id}'{batch_hint}. Say vendor, total, currency ONLY. One sentence max.]"
                            ) if grounding else (
                                f"[System: Invoice '{invoice_id}'{batch_hint}. Read visually. One sentence max.]"
                            )

                            live_queue.send_content(
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part(inline_data=types.Blob(mime_type=mime, data=image_bytes)),
                                        types.Part.from_text(text=context_text),
                                    ],
                                )
                            )
                        else:
                            # Flow B: Gemini sees image first, grounding comes later
                            logger.info(f"Flow B: image #{count} sent, awaiting grounding")
                            live_queue.send_content(
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part(inline_data=types.Blob(mime_type=mime, data=image_bytes)),
                                        types.Part.from_text(
                                            text=f"[System: Invoice photo{batch_hint}. Say vendor and total ONLY. One sentence. Do not repeat previous invoices.]"
                                        ),
                                    ],
                                )
                            )

                    elif msg_type == "grounding":
                        # Flow B step 2: Document AI grounding arrives
                        invoice_id = data.get("invoice_id", "unknown")
                        invoice = invoice_store.get(invoice_id, {})
                        grounding = invoice.get("grounding_text")
                        logger.info(f"Grounding received for invoice {invoice_id}")

                        # Check for flags that warrant agent speaking
                        result_data = data.get("data", {})
                        flags = []
                        if result_data.get("is_duplicate"):
                            flags.append("DUPLICATE")
                        fraud = result_data.get("fraud_check", {})
                        if fraud.get("risk_level") in ("CRITICAL", "HIGH"):
                            warnings = result_data.get("fraud_warning", [])
                            flags.append(f"Fraud {fraud.get('risk_level')}: {'; '.join(warnings) if warnings else 'flagged'}")

                        if grounding and flags:
                            # Only speak for flags — duplicate, fraud, etc.
                            context_text = (
                                f"{grounding}\n\n"
                                f"[System: ALERT for {invoice_id}: {' | '.join(flags)}. "
                                f"One sentence only. Saturday is normal for restaurants/retail.]"
                            )
                            live_queue.send_content(
                                types.Content(
                                    role="user",
                                    parts=[types.Part.from_text(text=context_text)],
                                )
                            )
                            logger.info(f"Grounding + flags sent for {invoice_id}: {flags}")
                        else:
                            # No flags — UI already shows the data, agent stays silent
                            logger.info(f"Grounding for {invoice_id}: no flags, UI only")

                    elif msg_type == "text":
                        logger.info(f"Text message: {data['data'][:100]}")
                        live_queue.send_content(
                            types.Content(
                                role="user",
                                parts=[types.Part.from_text(text=data["data"])],
                            )
                        )

        except WebSocketDisconnect:
            logger.info(f"Client disconnected (upstream): user={user_id}")
        except Exception as e:
            logger.error(f"Upstream error: {e}\n{traceback.format_exc()}")
        finally:
            live_queue.close()

    # Signal: upstream sets this when first message arrives
    first_message = asyncio.Event()

    async def downstream():
        """Stream Gemini responses back to the client."""
        # Wait for the first message before starting Live API
        # This prevents the Live API from timing out while user is idle
        logger.info(f"Waiting for first message from user={user_id}")
        await first_message.wait()
        logger.info(f"First message received, starting Live API for user={user_id}")

        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Aoede"
                    )
                ),
                language_code="en-US",
            ),
            response_modalities=["AUDIO"],
            output_audio_transcription=types.AudioTranscriptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                async for event in runner.run_live(
                    user_id=user_id,
                    session_id=session_id,
                    live_request_queue=live_queue,
                    run_config=run_config,
                ):
                    if not event:
                        continue

                    # Transcription events (separate from content/audio)
                    # These have event.content=None, so must be checked first
                    if hasattr(event, "output_transcription") and event.output_transcription and event.output_transcription.text:
                        await websocket.send_text(
                            json.dumps({"type": "transcript", "data": event.output_transcription.text})
                        )
                        tracker.record_voice_turn()

                    if hasattr(event, "input_transcription") and event.input_transcription and event.input_transcription.text:
                        await websocket.send_text(
                            json.dumps({"type": "user_transcript", "data": event.input_transcription.text})
                        )

                    if not event.content or not event.content.parts:
                        continue

                    for part in event.content.parts:
                        # Check for overlay commands from the agent
                        while _overlay_commands:
                            cmd = _overlay_commands.pop(0)
                            await websocket.send_text(
                                json.dumps({"type": "overlay", **cmd})
                            )

                        if part.inline_data:
                            await websocket.send_bytes(part.inline_data.data)

                # Clean exit from run_live — no retry needed
                break

            except WebSocketDisconnect:
                logger.info(f"Client disconnected (downstream): user={user_id}")
                return
            except Exception as e:
                logger.warning(f"Live API error (attempt {attempt+1}/{max_retries}): {e}")
                try:
                    if attempt < max_retries - 1:
                        await websocket.send_text(
                            json.dumps({"type": "status", "data": "Reconnecting..."})
                        )
                        await asyncio.sleep(1)
                        # Re-inject session context on reconnect
                        summary = tracker.get_session_summary()
                        if summary:
                            live_queue.send_content(
                                types.Content(
                                    role="user",
                                    parts=[types.Part.from_text(
                                        text=f"[System: Session reconnected. Context summary: {summary}]"
                                    )],
                                )
                            )
                    else:
                        logger.error(f"Live API failed after {max_retries} attempts")
                        await websocket.send_text(
                            json.dumps({"type": "status", "data": "Connection lost. Please refresh."})
                        )
                except Exception:
                    logger.info("Client WebSocket already closed, stopping retries")
                    return

    await asyncio.gather(upstream(), downstream())
    logger.info(f"Session ended: user={user_id} session={session_id}")


# ── Static Files (must be last) ──────────────────────────────────────────

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8002))
    http_port = port + 1  # HTTP on 8003

    cert_dir = os.path.dirname(__file__)
    cert_file = os.path.join(cert_dir, "titan.tail2e1adb.ts.net.crt")
    key_file = os.path.join(cert_dir, "titan.tail2e1adb.ts.net.key")

    ssl_kwargs = {}
    if os.path.exists(cert_file) and os.path.exists(key_file):
        ssl_kwargs["ssl_certfile"] = cert_file
        ssl_kwargs["ssl_keyfile"] = key_file
        logger.info(f"HTTPS: https://0.0.0.0:{port}")
        logger.info(f"HTTP:  http://0.0.0.0:{http_port} (use Chrome flag for camera)")

        # Run both HTTP and HTTPS
        import threading
        threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={"host": "0.0.0.0", "port": http_port},
            daemon=True,
        ).start()
    else:
        logger.info(f"HTTP only: http://0.0.0.0:{port}")

    uvicorn.run(app, host="0.0.0.0", port=port, **ssl_kwargs)
