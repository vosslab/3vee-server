#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PY_ROOT}"

# Run pyflakes on all Python files and capture output, excluding pyami
pyflakes $(find "${PY_ROOT}" -path "${PY_ROOT}/pyami" -prune -o -name "*.py" -print) > pyflakes.txt 2>&1 || true

RESULT=$(wc -l < pyflakes.txt)

echo "Found ${RESULT} pyflakes errors"

# Fail if any errors were found
if [ "${RESULT}" -ne 0 ]; then
    exit 1
fi
