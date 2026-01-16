import pathlib
import sys

import numpy


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PY_ROOT = REPO_ROOT / "py"
if str(PY_ROOT) not in sys.path:
	sys.path.insert(0, str(PY_ROOT))

from pyami import arraystats


#============================================
def test_all_stats_values() -> None:
	data = numpy.array([1.0, 2.0, 3.0, 4.0])
	stats = arraystats.all(data)
	assert stats["min"] == 1.0
	assert stats["max"] == 4.0
	assert numpy.isclose(stats["mean"], 2.5)
	assert numpy.isclose(stats["std"], numpy.std(data))


#============================================
def test_cached_stats_force() -> None:
	data = numpy.array([1.0, 2.0, 3.0, 4.0])
	mean_initial = arraystats.mean(data)
	data[:] = 10.0
	mean_cached = arraystats.mean(data)
	mean_forced = arraystats.mean(data, force=True)
	assert numpy.isclose(mean_cached, mean_initial)
	assert numpy.isclose(mean_forced, 10.0)
