import pathlib
import sys

import pytest


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PY_ROOT = REPO_ROOT / "py"
if str(PY_ROOT) not in sys.path:
	sys.path.insert(0, str(PY_ROOT))

from pyami import weakattr


class _Thing:
	pass


#============================================
def test_set_get() -> None:
	obj = _Thing()
	weakattr.set(obj, "alpha", 123)
	assert weakattr.get(obj, "alpha") == 123


#============================================
def test_get_missing_raises() -> None:
	obj = _Thing()
	with pytest.raises(AttributeError):
		weakattr.get(obj, "missing")
