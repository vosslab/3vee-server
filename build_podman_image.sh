#!/usr/bin/env bash
set -euo pipefail

#podman machine init --cpus 4 --memory 10240 --now --user-mode-networking

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${REPO_ROOT}"

LOG_DIR="logs"

ARCH=""
IMAGE_NAME="threev-web"
IMAGE_TAG="latest"
PODMAN_BUILD_PRIVILEGED="0"

usage() {
  printf '%s\n' \
    "Usage: build_podman_image.sh [options]" \
    "" \
    "Options:" \
    "  --arch <arch>            Podman build arch (default: native)" \
    "  --image-name <name>      Image name (default: threev-web)" \
    "  --image-tag <tag>        Image tag (default: latest)" \
    "  --log-dir <dir>          Log directory (default: logs)" \
    "  --privileged-build       Use --privileged for podman build" \
    "  --help                   Show this help"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --arch)
      ARCH="${2:-}"
      shift 2
      ;;
    --image-name)
      IMAGE_NAME="${2:-}"
      shift 2
      ;;
    --image-tag)
      IMAGE_TAG="${2:-}"
      shift 2
      ;;
    --log-dir)
      LOG_DIR="${2:-logs}"
      shift 2
      ;;
    --privileged-build)
      PODMAN_BUILD_PRIVILEGED="1"
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "$LOG_DIR"

timestamp="$(date +%Y%m%d-%H%M%S)"
log_file="${LOG_DIR}/podman-compose-${timestamp}.log"

echo "Building ${IMAGE_NAME}:${IMAGE_TAG} (ARCH=${ARCH:-native}, PRIVILEGED=${PODMAN_BUILD_PRIVILEGED})"
if [ -n "${ARCH}" ]; then
  build_args=(--arch "${ARCH}" -t "${IMAGE_NAME}:${IMAGE_TAG}" .)
else
  build_args=(-t "${IMAGE_NAME}:${IMAGE_TAG}" .)
fi
if [ "${PODMAN_BUILD_PRIVILEGED}" = "1" ]; then
  build_args=(--privileged "${build_args[@]}")
fi
podman build "${build_args[@]}"

# Clean out old containers, keep DB data
podman compose down

# Start db in background
WEB_IMAGE_NAME="${IMAGE_NAME}" WEB_IMAGE_TAG="${IMAGE_TAG}" podman compose up -d db

echo "Logging podman compose output to ${log_file}"
WEB_IMAGE_NAME="${IMAGE_NAME}" WEB_IMAGE_TAG="${IMAGE_TAG}" podman compose up web 2>&1 | tee "${log_file}"
