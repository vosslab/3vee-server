import pathlib
import sys

import numpy


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PY_ROOT = REPO_ROOT / "py"
if str(PY_ROOT) not in sys.path:
	sys.path.insert(0, str(PY_ROOT))

import mrcTrim


#============================================
def test_get_cutoff_simple() -> None:
	linedensity = numpy.array([0.0, 0.0, 3.0, 3.0])
	cutoff = mrcTrim.getCutoff(linedensity)
	assert numpy.isclose(cutoff, 1.0)


#============================================
def test_get_percent_cut_manual() -> None:
	linedensity = numpy.arange(10, dtype=float)
	maxi, mini = mrcTrim.getPercentCut(linedensity, 0.2)
	assert maxi == 8.0
	assert mini == 2.0


#============================================
def test_get_percent_cut_auto_full_span() -> None:
	linedensity = numpy.array([0.0, 0.0, 5.0, 0.0, 0.0])
	maxi, mini = mrcTrim.getPercentCut(linedensity, 0.0)
	assert maxi == 4
	assert mini == 0
