#!/usr/bin/env bash
set -euo pipefail

# Fetch the Chimera installer onto the host so Docker builds can COPY it
# directly instead of redownloading during each image build.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHIMERA_BIN="${REPO_ROOT}/docker/chimera.bin"
CHIMERA_FILE="linux_x86_64_osmesa/chimera-1.19-linux_x86_64_osmesa.bin"

log() {
	echo "[prefetch-assets] $*"
}

file_size_bytes() {
	local path="$1"
	if [ ! -e "${path}" ]; then
		echo 0
		return
	fi
	if stat -f %z "${path}" >/dev/null 2>&1; then
		stat -f %z "${path}"
		return
	elif stat -c %s "${path}" >/dev/null 2>&1; then
		stat -c %s "${path}"
		return
	fi
	wc -c < "${path}" | tr -d '[:space:]'
}

prefetch_chimera() {
	if [ -s "${CHIMERA_BIN}" ]; then
		size=$(file_size_bytes "${CHIMERA_BIN}")
		log "Chimera installer already present at docker/chimera.bin (${size} bytes)"
		return
	fi
	log "Downloading Chimera installer to docker/chimera.bin"
	python3 "${REPO_ROOT}/docker/download_chimera_headless.py" \
		--file "${CHIMERA_FILE}" \
		--output "${CHIMERA_BIN}"
	chmod +x "${CHIMERA_BIN}"
	size=$(file_size_bytes "${CHIMERA_BIN}")
	log "Saved docker/chimera.bin (${size} bytes)"
}

prefetch_chimera
