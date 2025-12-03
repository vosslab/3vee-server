#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHP_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PHP_ROOT}"
echo "Linting PHP files under ${PHP_ROOT}"

if ! command -v php >/dev/null 2>&1; then
	echo "php executable not found in PATH" >&2
	echo "Search PATH: ${PATH}" >&2
	exit 1
fi

lint_targets() {
	find "${PHP_ROOT}" -maxdepth 4 -type f \( -name '*.php' -o -name '*.inc' \) \
		-not -path '*/output/*'
}

status=0
count=0

while IFS= read -r file; do
	if [ -z "$file" ]; then
		continue
	fi
	if ! php -l "$file" >/dev/null; then
		echo "Lint failed: ${file}"
		status=1
	fi
	count=$((count + 1))
done < <(lint_targets)

echo "php -l checked ${count} files"
exit "${status}"
