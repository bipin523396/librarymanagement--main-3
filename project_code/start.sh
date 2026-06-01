#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "Starting BOOK HUB on 0.0.0.0:${PORT:-10000}"
exec gunicorn bookhub_backend.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
