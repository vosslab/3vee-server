#!/bin/sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUTPUT_DIR="${REPO_ROOT}/output"
PY_DIR="${REPO_ROOT}/py"

sleep 1
rm -fv "${OUTPUT_DIR}/running/runlog-test1.html"
rm -fvr "${OUTPUT_DIR}/results/test1/"
sleep 1
python3 "${PY_DIR}/runFSVCalc.py" --jobid=test1 --pdbid=1ehz
