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
NO_CACHE="0"

usage() {
  printf '%s\n' \
    "Usage: build_podman_image.sh [options]" \
    "" \
    "Options:" \
    "  --arch <arch>            Podman build arch (default: native)" \
    "  --image-name <name>      Image name (default: threev-web)" \
    "  --image-tag <tag>        Image tag (default: latest)" \
    "  --log-dir <dir>          Log directory (default: logs)" \
    "  --no-cache               Rebuild all layers from scratch" \
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
    --no-cache)
      NO_CACHE="1"
      shift
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

THREEV_VERSION="unknown"
if [ -f "${REPO_ROOT}/VERSION" ]; then
  THREEV_VERSION="$(cat "${REPO_ROOT}/VERSION" | tr -d '[:space:]')"
fi

echo "Building ${IMAGE_NAME}:${IMAGE_TAG} v${THREEV_VERSION} (ARCH=${ARCH:-native}, PRIVILEGED=${PODMAN_BUILD_PRIVILEGED})"
if [ -n "${ARCH}" ]; then
  build_args=(--build-arg "THREEV_VERSION=${THREEV_VERSION}" --arch "${ARCH}" -t "${IMAGE_NAME}:${IMAGE_TAG}" .)
else
  build_args=(--build-arg "THREEV_VERSION=${THREEV_VERSION}" -t "${IMAGE_NAME}:${IMAGE_TAG}" .)
fi
if [ "${PODMAN_BUILD_PRIVILEGED}" = "1" ]; then
  build_args=(--privileged "${build_args[@]}")
fi
if [ "${NO_CACHE}" = "1" ]; then
  build_args=(--no-cache "${build_args[@]}")
fi
podman build "${build_args[@]}"

# Clean out old containers and stale pods
echo "Cleaning up old containers..."
podman compose down 2>/dev/null || true
# Remove stale pods that can cause "proxy already running" errors
for pod in $(podman pod ls --format '{{.Name}}' 2>/dev/null | grep '3vee-server' || true); do
  echo "  removing stale pod: ${pod}"
  podman pod rm -f "${pod}" 2>/dev/null || true
done
# Remove any orphaned containers from previous runs
for ctr in $(podman ps -a --format '{{.Names}}' 2>/dev/null | grep '3vee-server' || true); do
  echo "  removing orphaned container: ${ctr}"
  podman rm -f "${ctr}" 2>/dev/null || true
done

# Remove dangling images from previous builds
podman image prune -f 2>/dev/null || true

# Ensure host output directories exist before the volume mount
mkdir -p "${REPO_ROOT}/output/uploads"

# Start services
export WEB_IMAGE_NAME="${IMAGE_NAME}"
export WEB_IMAGE_TAG="${IMAGE_TAG}"

echo "Starting db..."
podman compose up -d db

echo "Logging podman compose output to ${log_file}"
podman compose up web 2>&1 | tee "${log_file}"
