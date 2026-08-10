#!/usr/bin/env bash
set -e

echo "Starting SAGE (native, air-gapped)..."

# Start API in background
(cd api && uv run uvicorn main:app --port 8000) &
API_PID=$!

# Give the API a moment to bind before web starts hammering it
sleep 1

cleanup() {
  echo ""
  echo "Shutting down SAGE..."
  kill "$API_PID" 2>/dev/null || true
  # Kill any child processes (e.g. npm's underlying node process)
  kill 0 2>/dev/null || true
  exit 0
}

trap cleanup SIGINT SIGTERM

echo "API running (PID $API_PID) — http://localhost:8000"
echo "Starting web..."

# Foreground — Ctrl+C here triggers trap above
(cd web && npm run dev)

cleanup