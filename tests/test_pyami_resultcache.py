import pathlib
import sys

import numpy


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PY_ROOT = REPO_ROOT / "py"
if str(PY_ROOT) not in sys.path:
	sys.path.insert(0, str(PY_ROOT))

from pyami import resultcache


#============================================
def test_put_get_roundtrip() -> None:
	cache = resultcache.ResultCache(1024)
	data = numpy.arange(4, dtype=numpy.uint8)
	cache.put("key", data)
	result = cache.get("key")
	assert numpy.array_equal(result, data)


#============================================
def test_respects_size_limit() -> None:
	cache = resultcache.ResultCache(16)
	data_a = numpy.arange(8, dtype=numpy.uint8)
	data_b = numpy.arange(8, dtype=numpy.uint8)
	cache.put("a", data_a)
	cache.put("b", data_b)
	strong_size, _ = cache.getsize()
	assert strong_size <= 16
