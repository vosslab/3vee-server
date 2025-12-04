#!/usr/bin/env bash
set -euo pipefail

#podman machine init --cpus 4 --memory 10240 --now --user-mode-networking

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${REPO_ROOT}"

LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "$LOG_DIR"

timestamp="$(date +%Y%m%d-%H%M%S)"
log_file="${LOG_DIR}/podman-compose-${timestamp}.log"

ARCH="${ARCH:-}"
IMAGE_NAME="${IMAGE_NAME:-threev-web}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "Building ${IMAGE_NAME}:${IMAGE_TAG} (ARCH=${ARCH:-native})"
if [ -n "${ARCH}" ]; then
  podman build --arch "${ARCH}" -t "${IMAGE_NAME}:${IMAGE_TAG}" .
else
  podman build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
fi

# Clean out old containers, keep DB data
podman compose down

# Start db in background
WEB_IMAGE_NAME="${IMAGE_NAME}" WEB_IMAGE_TAG="${IMAGE_TAG}" podman compose up -d db

echo "Logging podman compose output to ${log_file}"
WEB_IMAGE_NAME="${IMAGE_NAME}" WEB_IMAGE_TAG="${IMAGE_TAG}" podman compose up web 2>&1 | tee "${log_file}"
