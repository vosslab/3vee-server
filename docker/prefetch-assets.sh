#!/usr/bin/env bash
set -euo pipefail

# Fetch third-party installers (Chimera + EMAN) onto the host so Docker builds
# can COPY them directly instead of redownloading during each image build.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHIMERA_BIN="${REPO_ROOT}/docker/chimera.bin"
CHIMERA_FILE="linux_x86_64_osmesa/chimera-1.19-linux_x86_64_osmesa.bin"
EMAN_TAR="${REPO_ROOT}/docker/eman-linux-x86_64-cluster-1.9.tar.gz"
EMAN_URL="https://github.com/leginon-org/appion-redmine-files/raw/refs/heads/main/eman-linux-x86_64-cluster-1.9.tar.gz"

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

download_with_progress() {
	local url="$1"
	local tmp="$2"
	rm -f "${tmp}"
	if command -v wget >/dev/null 2>&1; then
		wget --progress=bar:force -O "${tmp}" "${url}"
	elif command -v curl >/dev/null 2>&1; then
		curl --fail --location --show-error --progress-bar "${url}" -o "${tmp}"
	else
		log "Neither curl nor wget is available to download ${url}"
		exit 1
	fi
	if [ ! -s "${tmp}" ]; then
		log "Download produced an empty file for ${url}"
		exit 1
	fi
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

prefetch_eman() {
	local basename
	basename=$(basename "${EMAN_TAR}")
	if [ -s "${EMAN_TAR}" ]; then
		size=$(file_size_bytes "${EMAN_TAR}")
		log "EMAN archive already present at docker/${basename} (${size} bytes)"
		return
	fi
	tmp="${EMAN_TAR}.tmp"
	log "Downloading EMAN archive to docker/${basename}"
	download_with_progress "${EMAN_URL}" "${tmp}"
	mv "${tmp}" "${EMAN_TAR}"
	size=$(file_size_bytes "${EMAN_TAR}")
	log "Saved docker/${basename} (${size} bytes)"
}

prefetch_chimera
prefetch_eman
