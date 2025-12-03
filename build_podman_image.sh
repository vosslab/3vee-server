#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "$LOG_DIR"

timestamp="$(date +%Y%m%d-%H%M%S)"
log_file="${LOG_DIR}/podman-compose-${timestamp}.log"

ARCH="${ARCH:-amd64}"
IMAGE_NAME="${IMAGE_NAME:-threev-web}"
IMAGE_TAG="${IMAGE_TAG:-${ARCH}}"

echo "Building ${IMAGE_NAME}:${IMAGE_TAG} for architecture ${ARCH}"
podman build --arch "${ARCH}" -t "${IMAGE_NAME}:${IMAGE_TAG}" .

# Clean out old containers, keep DB data
podman compose down

# Start db in background
WEB_IMAGE_NAME="${IMAGE_NAME}" WEB_IMAGE_TAG="${IMAGE_TAG}" podman compose up -d db

echo "Logging podman compose output to ${log_file}"
WEB_IMAGE_NAME="${IMAGE_NAME}" WEB_IMAGE_TAG="${IMAGE_TAG}" podman compose up web 2>&1 | tee "${log_file}"
