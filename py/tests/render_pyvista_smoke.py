#!/usr/bin/env python3
"""
Headless renderer smoke test for 3Vee.
Runs a snapshot (and optional animation) on a test MRC with the selected renderer.
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path

from appionlib import apHeadlessRender


def _default_mplconfigdir():
	tmp = Path(tempfile.gettempdir()) / "mplconfig-3vee"
	tmp.mkdir(parents=True, exist_ok=True)
	return str(tmp)


def parse_args():
	base_dir = Path(__file__).resolve().parent
	default_volume = base_dir / "2LYZ-test_volume.mrc"
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--volume", type=Path, default=default_volume, help="Path to MRC volume.")
	parser.add_argument("--pdb", type=Path, default=None, help="Optional PDB to overlay.")
	parser.add_argument("--renderer", choices=["pyvista", "mpl"], default="pyvista", help="Renderer backend.")
	parser.add_argument("--imgsize", type=int, default=256, help="Image size (square, px).")
	parser.add_argument("--contour", type=float, default=None, help="Marching cubes contour; defaults to heuristic.")
	parser.add_argument("--silhouette", action=argparse.BooleanOptionalAction, default=True, help="Enable silhouette/outline.")
	parser.add_argument("--animation", action="store_true", help="Also render GIF spin.")
	parser.add_argument("--mplconfigdir", type=Path, default=None, help="Override MPLCONFIGDIR (useful on CI/headless).")
	return parser.parse_args()


def main():
	args = parse_args()

	if not args.volume.is_file():
		sys.stderr.write(f"[error] volume not found: {args.volume}\n")
		return 1
	if args.pdb and not args.pdb.is_file():
		sys.stderr.write(f"[error] pdb not found: {args.pdb}\n")
		return 1

	if args.mplconfigdir:
		os.environ["MPLCONFIGDIR"] = str(args.mplconfigdir)
	elif "MPLCONFIGDIR" not in os.environ:
		os.environ["MPLCONFIGDIR"] = _default_mplconfigdir()

	if args.renderer == "pyvista":
		os.environ["THREEV_RENDERER"] = "pyvista"
	else:
		os.environ.pop("THREEV_RENDERER", None)
		os.environ.pop("THREEV_USE_PYVISTA", None)

	out_base = args.volume.with_suffix("")
	print(f"[info] volume: {args.volume}")
	if args.pdb:
		print(f"[info] pdb: {args.pdb}")
	print(f"[info] renderer: {args.renderer}")
	print(f"[info] output base: {out_base}")
	print(f"[info] silhouette: {args.silhouette}")
	print(f"[info] imgsize: {args.imgsize}")

	try:
		apHeadlessRender.renderSnapshots(
			str(args.volume),
			contour=args.contour,
			silhouette=args.silhouette,
			pdb=str(args.pdb) if args.pdb else None,
			name=str(out_base),
		)
		if args.animation:
			apHeadlessRender.renderAnimation(
				str(args.volume),
				contour=args.contour,
				silhouette=args.silhouette,
				pdb=str(args.pdb) if args.pdb else None,
				name=str(out_base),
			)
	except Exception as exc:
		sys.stderr.write(f"[error] render failed: {exc}\n")
		return 2

	print("[info] render complete")
	return 0


if __name__ == "__main__":
	sys.exit(main())
