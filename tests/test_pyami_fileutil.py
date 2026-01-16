import pathlib
import sys


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PY_ROOT = REPO_ROOT / "py"
if str(PY_ROOT) not in sys.path:
	sys.path.insert(0, str(PY_ROOT))

from pyami import fileutil


#============================================
def test_open_if_not_exists(tmp_path: pathlib.Path) -> None:
	target = tmp_path / "fresh.txt"
	handle = fileutil.open_if_not_exists(str(target))
	handle.write("ok")
	handle.close()
	with open(target, "r") as read_handle:
		assert read_handle.read() == "ok"


#============================================
def test_remove_all_files_in_dir_counts_subdirs(tmp_path: pathlib.Path) -> None:
	(tmp_path / "a.txt").write_text("a")
	(tmp_path / "b.txt").write_text("b")
	(tmp_path / "subdir").mkdir()
	count = fileutil.remove_all_files_in_dir(str(tmp_path))
	assert count == 1
	assert not (tmp_path / "a.txt").exists()
	assert not (tmp_path / "b.txt").exists()


#============================================
def test_check_exist_one_file_selects_last(tmp_path: pathlib.Path) -> None:
	first = tmp_path / "first.cfg"
	second = tmp_path / "second.cfg"
	first.write_text("one")
	second.write_text("two")
	result = fileutil.check_exist_one_file([str(first), str(second)], combine=False)
	assert result == [str(second)]
