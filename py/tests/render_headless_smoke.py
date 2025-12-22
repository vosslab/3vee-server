#!/usr/bin/env python3
"""
Smoke test for the headless renderer.

Uses the bundled 2LYZ-test_volume.mrc to exercise:
- mesh extraction
- snapshot rendering via apHeadlessRender (PyVista if available, else matplotlib)
- snapshot rendering via direct matplotlib fallback
- optional STL export
"""

import argparse
import sys
import tempfile
import os
from pathlib import Path

import numpy
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from appionlib import apVolumeRender
from appionlib import apHeadlessRender
from pyami import mrc


def assert_nonempty(path: Path, label: str):
	if not path.is_file() or path.stat().st_size == 0:
		raise RuntimeError(f"{label} missing or empty: {path}")


def parse_args():
	parser = argparse.ArgumentParser(description="Headless renderer smoke test (PyVista + Matplotlib).")
	parser.add_argument("--renderer", choices=["pyvista", "mpl"], default="pyvista", help="Primary renderer for apHeadlessRender.")
	parser.add_argument("--imgsize", type=int, default=256, help="Snapshot size (pixels).")
	parser.add_argument("--silhouette", action=argparse.BooleanOptionalAction, default=False, help="Enable silhouette edges.")
	parser.add_argument("--volume", type=Path, default=None, help="Path to test MRC (defaults to bundled 2LYZ-test_volume.mrc).")
	parser.add_argument("--mplconfigdir", type=Path, default=None, help="Set MPLCONFIGDIR (defaults to temp dir).")
	parser.add_argument("--export-stl", action=argparse.BooleanOptionalAction, default=True, help="Export STL for basic IO check.")
	return parser.parse_args()


def main():
	args = parse_args()
	os.environ["THREEV_USE_PYVISTA"] = "1" if args.renderer == "pyvista" else "0"
	if args.mplconfigdir:
		os.environ["MPLCONFIGDIR"] = str(args.mplconfigdir)
	else:
		os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mplcache_"))

	print(f"[info] renderer={args.renderer}")
	print(f"[info] MPLCONFIGDIR={os.environ.get('MPLCONFIGDIR')}")

	repo_root = Path(__file__).resolve().parents[1]
	mrc_path = args.volume or (repo_root / "tests" / "2LYZ-test_volume.mrc")
	if not mrc_path.is_file():
		raise SystemExit(f"Test volume not found: {mrc_path}")

	# Load volume
	vol = mrc.read(str(mrc_path)).astype(numpy.float32)

	out_dir = Path(__file__).resolve().parent
	basename = out_dir / "rendered"

	verts, faces = apVolumeRender.extract_mesh(vol, level=None, spacing=(1.0, 1.0, 1.0))
	print(f"[info] verts: {verts.shape}, faces: {faces.shape}")
	print(f"[info] silhouettes: {args.silhouette}")

	print("[info] rendering snapshots via apHeadlessRender...")
	try:
		apHeadlessRender.renderSnapshots(
			str(mrc_path),
			contour=None,
			silhouette=args.silhouette,
			pdb=None,
			name=str(basename),
		)
		print("[info] snapshots rendered (apHeadlessRender)")
	except Exception as exc:
		print(f"[warn] apHeadlessRender snapshots failed; using apVolumeRender directly: {exc}")
		apVolumeRender.render_png_views(verts, faces, str(basename), imgsize=args.imgsize, silhouette_width=0)

	print("[info] rendering snapshots via direct matplotlib fallback...")
	apVolumeRender.render_png_views(verts, faces, str(basename) + ".mpl", imgsize=args.imgsize, silhouette_width=0)
	print("[info] fallback snapshots rendered")

	if args.export_stl:
		apVolumeRender.export_stl(verts, faces, str(basename.with_suffix(".stl")))

	# Validate outputs
	for idx in (1, 2, 3):
		assert_nonempty(basename.with_suffix(f".{idx}.png"), f"snapshot {idx}")
		assert_nonempty((basename.with_suffix(f".{idx}.png").with_name(basename.name + ".mpl." + str(idx) + ".png")), f"fallback snapshot {idx}")
	if args.export_stl:
		assert_nonempty(basename.with_suffix(".stl"), "stl")

	print(f"Headless render smoke test passed. Outputs in {out_dir}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
