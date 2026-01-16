import pathlib
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PY_ROOT = REPO_ROOT / "py"
if str(PY_ROOT) not in sys.path:
	sys.path.insert(0, str(PY_ROOT))

from pyami import ordereddict


#============================================
def test_insertion_order() -> None:
	ordered = ordereddict.OrderedDict()
	ordered["b"] = 2
	ordered["a"] = 1
	assert ordered.keys() == ["b", "a"]


#============================================
def test_update_preserves_existing_order() -> None:
	ordered = ordereddict.OrderedDict([("a", 1)])
	ordered.update({"b": 2, "a": 3})
	assert ordered.keys() == ["a", "b"]


#============================================
def test_str_order() -> None:
	ordered = ordereddict.OrderedDict([("x", 1), ("y", 2)])
	assert str(ordered) == "{x: 1, y: 2}"
