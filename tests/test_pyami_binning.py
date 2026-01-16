import pathlib
import sys

import numpy
import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PY_ROOT = REPO_ROOT / "py"
if str(PY_ROOT) not in sys.path:
	sys.path.insert(0, str(PY_ROOT))

from pyami import binning


#============================================
def test_bin3_mean() -> None:
	data = numpy.arange(8, dtype=float).reshape((2, 2, 2))
	binned = binning.bin3(data, 2)
	assert binned.shape == (1, 1, 1)
	assert numpy.isclose(binned[0, 0, 0], 3.5)


#============================================
def test_bin3_invalid_factor() -> None:
	with pytest.raises(ValueError):
		binning.bin3(numpy.zeros((2, 2, 2)), 0)


#============================================
def test_bin3_invalid_ndim() -> None:
	with pytest.raises(ValueError):
		binning.bin3(numpy.zeros((2, 2)), 2)


#============================================
def test_bin3f_invalid_ndim() -> None:
	with pytest.raises(ValueError):
		binning.bin3f(numpy.zeros((2, 2)), 2)
