#!/usr/bin/env bash
#
# Deploy InvoiceScan AI to Google Cloud Run
#
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────────────────
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:?Set GOOGLE_CLOUD_PROJECT env var}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="invoicescan-ai"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# ── Set active project ───────────────────────────────────────────────────
echo "==> Setting project to ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"

# ── Build with Cloud Build ───────────────────────────────────────────────
echo "==> Building container image with Cloud Build..."
gcloud builds submit \
  --tag "${IMAGE}" \
  --project "${PROJECT_ID}" \
  ../server

# ── Deploy to Cloud Run ──────────────────────────────────────────────────
echo "==> Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_GENAI_USE_VERTEXAI=true" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --set-env-vars "GOOGLE_CLOUD_LOCATION=us-central1" \
  --set-env-vars "DOCAI_PROCESSOR_ID=${DOCAI_PROCESSOR_ID:?Set DOCAI_PROCESSOR_ID}" \
  --set-env-vars "DOCAI_LOCATION=${DOCAI_LOCATION:-us}" \
  --set-env-vars "GEMINI_MODEL=gemini-2.5-flash" \
  --set-env-vars "VERTEX_SEARCH_LOCATION=global" \
  --set-env-vars "VERTEX_SEARCH_DATA_STORE_ID=${VERTEX_SEARCH_DATA_STORE_ID:-}" \
  --set-env-vars "VERTEX_SEARCH_ENGINE_ID=${VERTEX_SEARCH_ENGINE_ID:-}" \
  --set-env-vars "SHEETS_SPREADSHEET_ID=${SHEETS_SPREADSHEET_ID:?Set SHEETS_SPREADSHEET_ID}" \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY:?Set GEMINI_API_KEY env var before deploying}" \
  --memory 1Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 3 \
  --timeout 300 \
  --port 8080

# ── Print service URL ────────────────────────────────────────────────────
echo ""
echo "==> Deployment complete!"
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format "value(status.url)")
echo "Service URL: ${SERVICE_URL}"
