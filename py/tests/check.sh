#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PY_ROOT}"

find "${PY_ROOT}" \( -name "*.pyo" -o -name "*.pyc" \) -delete

echo ""
echo "Trying to import all libraries"
echo "----------------"
rm -f importer.py
{
	echo "#!/usr/bin/env python3"
	echo "from pyami import quietscipy"
	for i in appionlib/*.py; do
		j=$(basename "$i" .py)
		echo "print('... ${j}')"
		echo "from appionlib import ${j}"
	done
	echo "import sys"
	echo "sys.stderr.write('\\n\\n** SUCCESS **\\n\\n')"
	echo "sys.exit(0)"
} > importer.py
chmod 775 importer.py
./importer.py
echo "----------------"
echo ""
echo ""

sleep 1

echo "Trying to import all binaries"
echo "----------------"
rm -f importer.py
{
	echo "#!/usr/bin/env python3"
	echo "from pyami import quietscipy"
	for i in *.py; do
		j=$(basename "$i" .py)
		echo "print('... ${j}')"
		echo "import ${j}"
	done
	echo "import sys"
	echo "sys.stderr.write('\\n\\n** SUCCESS **\\n\\n')"
	echo "sys.exit(0)"
} > importer.py
chmod 775 importer.py
./importer.py
echo "----------------"
echo ""
echo ""

sleep 1
rm -fv importer.py
