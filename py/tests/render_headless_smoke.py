#!/usr/bin/env python3
"""
Smoke test for the headless renderer.

Uses the bundled 2LYZ-test_volume.mrc to exercise:
- mesh extraction
- snapshot rendering
- animation GIF rendering
- optional STL export
"""

import sys
import tempfile
import os
from pathlib import Path

import numpy
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from appionlib import apVolumeRender
from pyami import mrc


def assert_nonempty(path: Path, label: str):
	if not path.is_file() or path.stat().st_size == 0:
		raise RuntimeError(f"{label} missing or empty: {path}")


def main():
	os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mplcache_"))
	repo_root = Path(__file__).resolve().parents[1]
	mrc_path = repo_root / "tests" / "2LYZ-test_volume.mrc"
	if not mrc_path.is_file():
		raise SystemExit(f"Test volume not found: {mrc_path}")

	# Load volume
	vol = mrc.read(str(mrc_path)).astype(numpy.float32)

	out_dir = Path(__file__).resolve().parent
	basename = out_dir / "rendered"

	verts, faces = apVolumeRender.extract_mesh(vol, level=None, spacing=(1.0, 1.0, 1.0))
	apVolumeRender.render_png_views(verts, faces, str(basename), imgsize=256)
	apVolumeRender.render_animation_gif(verts, faces, str(basename), imgsize=256, n_frames=12)
	apVolumeRender.export_stl(verts, faces, str(basename.with_suffix(".stl")))

	# Validate outputs
	for idx in (1, 2, 3):
		assert_nonempty(basename.with_suffix(f".{idx}.png"), f"snapshot {idx}")
	assert_nonempty(basename.with_suffix(".animate.gif"), "animation")
	assert_nonempty(basename.with_suffix(".stl"), "stl")

	print(f"Headless render smoke test passed. Outputs in {out_dir}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
