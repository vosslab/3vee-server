#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "$LOG_DIR"

timestamp="$(date +%Y%m%d-%H%M%S)"
log_file="${LOG_DIR}/podman-compose-${timestamp}.log"

# Clean out old containers, keep DB data
podman compose down

# Start db in background
podman compose up -d db

echo "Logging podman compose output to ${log_file}"
podman compose up --build web 2>&1 | tee "${log_file}"
