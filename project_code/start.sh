#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-10000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
WEB_THREADS="${WEB_THREADS:-2}"
GUNICORN_MAX_REQUESTS="${GUNICORN_MAX_REQUESTS:-1000}"
GUNICORN_MAX_REQUESTS_JITTER="${GUNICORN_MAX_REQUESTS_JITTER:-100}"
GUNICORN_WORKER_TMP_DIR="${GUNICORN_WORKER_TMP_DIR:-/tmp}"

echo "Starting BOOK HUB on 0.0.0.0:${PORT} with ${WEB_CONCURRENCY} workers and ${WEB_THREADS} threads"
exec gunicorn bookhub_backend.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --threads "${WEB_THREADS}" \
  --timeout 120 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --max-requests "${GUNICORN_MAX_REQUESTS}" \
  --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER}" \
  --worker-tmp-dir "${GUNICORN_WORKER_TMP_DIR}" \
  --access-logfile - \
  --error-logfile -
