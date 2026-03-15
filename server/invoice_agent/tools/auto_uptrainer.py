"""Auto-uptraining pipeline — fields graduate from Gemini to Document AI.

The self-improving loop:
1. User teaches agent a custom field → Gemini Vision extracts it (Layer 2)
2. Each extraction = an implicit label (if user doesn't correct it)
3. When 50+ clean samples accumulate → trigger Document AI uptraining
4. New processor version deployed → field is now grounded (Layer 1)

No manual labeling. No annotation workbench. The agent's daily work
generates the training data automatically.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from ..config import GCP_PROJECT, DOCAI_LOCATION, DOCAI_PROCESSOR_ID, DOCAI_ENABLED

logger = logging.getLogger(__name__)

# Thresholds
MIN_SAMPLES_FOR_TRAINING = 50
MIN_ACCURACY_RATE = 0.85  # 85% of samples must be user-approved (not corrected)
TRAINING_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "training_data")


@dataclass
class LabeledSample:
    """A single labeled sample for uptraining."""
    invoice_id: str
    image_path: str
    mime_type: str
    field_name: str
    extracted_value: str
    extraction_method: str  # "gemini" or "user_corrected"
    user_approved: bool  # True = no correction, False = user said it's wrong
    corrected_value: Optional[str] = None  # If user corrected it
    timestamp: str = ""
    # Document AI text anchors (for bounding box matching)
    text_anchor_start: Optional[int] = None
    text_anchor_end: Optional[int] = None


@dataclass
class FieldTrainingStatus:
    """Tracks training readiness for a custom field."""
    field_name: str
    total_samples: int = 0
    approved_samples: int = 0
    corrected_samples: int = 0
    rejected_samples: int = 0
    accuracy_rate: float = 0.0
    ready_for_training: bool = False
    training_triggered: bool = False
    graduated_to_docai: bool = False
    last_updated: str = ""


# In-memory stores (would be persistent DB in production)
_sample_store: dict[str, list[LabeledSample]] = {}  # field_name -> [samples]
_field_status: dict[str, FieldTrainingStatus] = {}


def _ensure_training_dir():
    """Create training data directory if needed."""
    os.makedirs(TRAINING_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(TRAINING_DATA_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(TRAINING_DATA_DIR, "labels"), exist_ok=True)


def _update_field_status(field_name: str) -> FieldTrainingStatus:
    """Recalculate training readiness for a field."""
    samples = _sample_store.get(field_name, [])

    total = len(samples)
    approved = sum(1 for s in samples if s.user_approved)
    corrected = sum(1 for s in samples if s.corrected_value is not None)
    rejected = sum(1 for s in samples if not s.user_approved and s.corrected_value is None)

    accuracy = approved / total if total > 0 else 0.0
    ready = total >= MIN_SAMPLES_FOR_TRAINING and accuracy >= MIN_ACCURACY_RATE

    status = FieldTrainingStatus(
        field_name=field_name,
        total_samples=total,
        approved_samples=approved,
        corrected_samples=corrected,
        rejected_samples=rejected,
        accuracy_rate=round(accuracy, 3),
        ready_for_training=ready,
        training_triggered=_field_status.get(field_name, FieldTrainingStatus(field_name=field_name)).training_triggered,
        graduated_to_docai=_field_status.get(field_name, FieldTrainingStatus(field_name=field_name)).graduated_to_docai,
        last_updated=datetime.now(timezone.utc).isoformat(),
    )

    _field_status[field_name] = status
    return status


# ── Sample Collection ─────────────────────────────────────────────────────


def record_extraction(
    invoice_id: str,
    field_name: str,
    extracted_value: str,
    image_path: str = "",
    mime_type: str = "image/jpeg",
    full_text: str = "",
) -> dict:
    """Record a Gemini Vision extraction as an implicit label.

    Called automatically after extract_custom_fields succeeds.
    The sample is marked as approved (user_approved=True) by default.
    If the user corrects it later, call correct_extraction().

    Args:
        invoice_id: The invoice ID.
        field_name: The extracted field name.
        extracted_value: The value Gemini extracted.
        image_path: Path to the stored invoice image.
        mime_type: Image MIME type.
        full_text: Document AI OCR text (for text anchor matching).

    Returns:
        Updated training status for this field.
    """
    field_name = field_name.lower().strip()

    if field_name not in _sample_store:
        _sample_store[field_name] = []

    # Find text anchor (where the value appears in OCR text)
    text_start = None
    text_end = None
    if full_text and extracted_value:
        idx = full_text.lower().find(extracted_value.lower())
        if idx >= 0:
            text_start = idx
            text_end = idx + len(extracted_value)

    sample = LabeledSample(
        invoice_id=invoice_id,
        image_path=image_path,
        mime_type=mime_type,
        field_name=field_name,
        extracted_value=extracted_value,
        extraction_method="gemini",
        user_approved=True,  # Implicit approval — user hasn't said it's wrong
        timestamp=datetime.now(timezone.utc).isoformat(),
        text_anchor_start=text_start,
        text_anchor_end=text_end,
    )

    _sample_store[field_name].append(sample)
    status = _update_field_status(field_name)

    logger.info(
        f"Recorded sample for '{field_name}': '{extracted_value}' "
        f"({status.total_samples}/{MIN_SAMPLES_FOR_TRAINING} toward training)"
    )

    # Check if we should trigger training
    if status.ready_for_training and not status.training_triggered:
        logger.info(
            f"Field '{field_name}' is ready for Document AI uptraining! "
            f"{status.approved_samples} approved samples, "
            f"{status.accuracy_rate:.0%} accuracy."
        )

    return {
        "field": field_name,
        "sample_recorded": True,
        "training_status": {
            "total": status.total_samples,
            "needed": MIN_SAMPLES_FOR_TRAINING,
            "approved": status.approved_samples,
            "accuracy": f"{status.accuracy_rate:.0%}",
            "ready": status.ready_for_training,
        },
    }


def correct_extraction(
    invoice_id: str,
    field_name: str,
    correct_value: str,
) -> dict:
    """Record a user correction — the Gemini extraction was wrong.

    When the user says "that's not right, the project code is actually XYZ",
    call this to mark the sample as corrected. The corrected value becomes
    the training label instead.

    Args:
        invoice_id: The invoice ID.
        field_name: The field that was wrong.
        correct_value: The correct value from the user.

    Returns:
        Updated training status.
    """
    field_name = field_name.lower().strip()
    samples = _sample_store.get(field_name, [])

    corrected = False
    for sample in samples:
        if sample.invoice_id == invoice_id:
            sample.user_approved = False
            sample.corrected_value = correct_value
            sample.extraction_method = "user_corrected"
            corrected = True
            break

    if not corrected:
        # User is providing a value we didn't extract — still a valid sample
        if field_name not in _sample_store:
            _sample_store[field_name] = []

        _sample_store[field_name].append(LabeledSample(
            invoice_id=invoice_id,
            image_path="",
            mime_type="",
            field_name=field_name,
            extracted_value=correct_value,
            extraction_method="user_provided",
            user_approved=True,
            timestamp=datetime.now(timezone.utc).isoformat(),
        ))

    status = _update_field_status(field_name)

    return {
        "field": field_name,
        "correction_recorded": True,
        "correct_value": correct_value,
        "training_status": {
            "total": status.total_samples,
            "needed": MIN_SAMPLES_FOR_TRAINING,
            "accuracy": f"{status.accuracy_rate:.0%}",
            "ready": status.ready_for_training,
        },
    }


# ── Training Status & Trigger ─────────────────────────────────────────────


def get_training_status(field_name: str = "") -> dict:
    """Check training readiness for custom fields.

    Shows how many samples have been collected, accuracy rate,
    and whether the field is ready for Document AI uptraining.

    Use this when the user asks "how is the learning going?" or
    "when will project_code be grounded?"

    Args:
        field_name: Specific field to check, or empty for all fields.

    Returns:
        Training status with sample counts and readiness.
    """
    if field_name:
        field_name = field_name.lower().strip()
        if field_name not in _sample_store:
            return {"field": field_name, "total_samples": 0, "message": "No samples yet."}
        status = _update_field_status(field_name)
        return {
            "field": field_name,
            "total_samples": status.total_samples,
            "approved_samples": status.approved_samples,
            "corrected_samples": status.corrected_samples,
            "accuracy_rate": f"{status.accuracy_rate:.0%}",
            "ready_for_training": status.ready_for_training,
            "graduated_to_docai": status.graduated_to_docai,
            "samples_needed": max(0, MIN_SAMPLES_FOR_TRAINING - status.total_samples),
            "progress": f"{min(status.total_samples, MIN_SAMPLES_FOR_TRAINING)}/{MIN_SAMPLES_FOR_TRAINING}",
        }

    # All fields
    all_status = {}
    for fn in _sample_store:
        s = _update_field_status(fn)
        all_status[fn] = {
            "samples": f"{s.total_samples}/{MIN_SAMPLES_FOR_TRAINING}",
            "accuracy": f"{s.accuracy_rate:.0%}",
            "ready": s.ready_for_training,
            "graduated": s.graduated_to_docai,
        }

    return {
        "fields": all_status,
        "total_fields_tracking": len(all_status),
        "ready_for_training": sum(1 for s in _field_status.values() if s.ready_for_training),
        "graduated": sum(1 for s in _field_status.values() if s.graduated_to_docai),
    }


def trigger_uptraining(field_name: str) -> dict:
    """Trigger Document AI uptraining for a field that has enough samples.

    This starts the uptraining process:
    1. Exports labeled samples to Document AI format
    2. Creates/updates the processor dataset
    3. Starts the training job
    4. On completion, deploys the new processor version

    Only call this when get_training_status shows ready_for_training=True.

    Args:
        field_name: The field to uptrain for.

    Returns:
        Training job status.
    """
    field_name = field_name.lower().strip()

    if field_name not in _field_status:
        return {"error": f"No training data for field '{field_name}'."}

    status = _field_status[field_name]
    if not status.ready_for_training:
        return {
            "error": f"Not ready. Need {MIN_SAMPLES_FOR_TRAINING} samples with "
                     f"{MIN_ACCURACY_RATE:.0%} accuracy. Currently: "
                     f"{status.total_samples} samples, {status.accuracy_rate:.0%} accuracy.",
        }

    if not DOCAI_ENABLED:
        return {"error": "Document AI not configured."}

    _ensure_training_dir()

    # Export samples for training
    samples = [s for s in _sample_store[field_name] if s.user_approved or s.corrected_value]
    export_path = os.path.join(TRAINING_DATA_DIR, "labels", f"{field_name}_labels.jsonl")

    with open(export_path, "w") as f:
        for sample in samples:
            label = {
                "invoice_id": sample.invoice_id,
                "field_name": sample.field_name,
                "value": sample.corrected_value or sample.extracted_value,
                "text_anchor_start": sample.text_anchor_start,
                "text_anchor_end": sample.text_anchor_end,
                "image_path": sample.image_path,
                "source": sample.extraction_method,
            }
            f.write(json.dumps(label) + "\n")

    logger.info(f"Exported {len(samples)} labeled samples to {export_path}")

    # In production: call Document AI API to create dataset + start training
    # For hackathon: log the readiness and provide instructions
    status.training_triggered = True
    _field_status[field_name] = status

    return {
        "status": "training_data_exported",
        "field": field_name,
        "samples_exported": len(samples),
        "export_path": export_path,
        "next_steps": {
            "message": (
                f"Training data for '{field_name}' is ready with {len(samples)} labeled samples. "
                f"To complete uptraining:"
            ),
            "steps": [
                f"1. Upload labeled documents to Document AI workbench",
                f"2. Add custom label '{field_name}' to the Invoice Parser schema",
                f"3. Import the labels from {export_path}",
                f"4. Start uptraining (takes 1-4 hours)",
                f"5. Deploy the new processor version",
                f"6. The field will then be extracted by Document AI (Layer 1) with full grounding",
            ],
            "api_endpoint": (
                f"https://{DOCAI_LOCATION}-documentai.googleapis.com/v1/"
                f"projects/{GCP_PROJECT}/locations/{DOCAI_LOCATION}/"
                f"processors/{DOCAI_PROCESSOR_ID}/processorVersions:train"
            ) if DOCAI_ENABLED else "Document AI not configured",
        },
    }


def graduate_field(field_name: str) -> dict:
    """Mark a field as graduated from Gemini (Layer 2) to Document AI (Layer 1).

    Call this after uptraining completes and the new processor version is deployed.
    The field will no longer need Gemini Vision extraction — Document AI handles it.

    Args:
        field_name: The field that has been uptrained.

    Returns:
        Confirmation of graduation.
    """
    field_name = field_name.lower().strip()

    if field_name in _field_status:
        _field_status[field_name].graduated_to_docai = True

    return {
        "status": "graduated",
        "field": field_name,
        "message": (
            f"Field '{field_name}' graduated to Document AI. "
            f"It will now be extracted with full grounding accuracy. "
            f"Gemini Vision extraction is no longer needed for this field."
        ),
    }
