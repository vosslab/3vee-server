#!/usr/bin/env python3
"""
Headless rendering via PyVista/VTK.
Renders iso-surfaces (verts/faces from marching cubes) with optional silhouette
overlay and optional PDB atoms in the same scene.
"""

from pathlib import Path
import math
import os

import numpy
from PIL import Image

from appionlib import apVolumeRender
from appionlib import apDisplay


def _require_pyvista():
	try:
		import pyvista as pv  # type: ignore
	except Exception as exc:
		raise ImportError("PyVista is required for this renderer") from exc
	return pv


def _faces_to_pyvista(faces):
	faces = numpy.asarray(faces, dtype=numpy.int64)
	if faces.size == 0:
		return faces
	tri_counts = numpy.full((faces.shape[0], 1), 3, dtype=numpy.int64)
	return numpy.hstack((tri_counts, faces)).ravel()


def _make_mesh(pv, verts, faces):
	mesh = pv.PolyData(verts, _faces_to_pyvista(faces))
	if not mesh.is_all_triangles:
		mesh = mesh.triangulate()
	try:
		mesh = mesh.compute_normals(
			auto_orient_normals=True,
			split_edges=False,
			inplace=False,
		)
	except TypeError:
		mesh = mesh.compute_normals(auto_orient_normals=True, inplace=False)
	return mesh


def _camera_position(mesh, elev, azim, distance_scale=1.8):
	length = mesh.length
	radius = length * distance_scale if length > 0 else distance_scale
	theta = math.radians(azim)
	phi = math.radians(90.0 - elev)
	x = radius * math.sin(phi) * math.cos(theta)
	y = radius * math.sin(phi) * math.sin(theta)
	z = radius * math.cos(phi)
	return [(x, y, z), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)]


def _pdb_atoms(pdb_path):
	points = []
	colors = []
	radii = []
	color_map = {
		"H": (0.9, 0.9, 0.9),
		"C": (0.25, 0.25, 0.25),
		"N": (0.0, 0.0, 0.8),
		"O": (0.8, 0.0, 0.0),
		"S": (0.9, 0.8, 0.1),
		"P": (0.9, 0.5, 0.1),
	}
	radius_map = {
		"H": 0.6,
		"C": 0.9,
		"N": 0.9,
		"O": 0.85,
		"S": 1.05,
		"P": 1.0,
	}
	try:
		with open(pdb_path, "r") as f:
			for line in f:
				if not line.startswith(("ATOM", "HETATM")):
					continue
				try:
					x = float(line[30:38])
					y = float(line[38:46])
					z = float(line[46:54])
				except Exception:
					continue
				elem = line[76:78].strip() or line[12:16].strip()[0]
				elem = elem[0].upper() if elem else "C"
				points.append((x, y, z))
				colors.append(color_map.get(elem, (0.5, 0.5, 0.5)))
				radii.append(radius_map.get(elem, 0.9))
	except OSError as exc:
		apDisplay.printWarning(f"Could not read PDB {pdb_path}: {exc}")
	return numpy.asarray(points, dtype=float), numpy.asarray(colors, dtype=float), numpy.asarray(radii, dtype=float)


def _add_atoms(plotter, pv, pdb_path):
	if pdb_path is None:
		return
	points, colors, radii = _pdb_atoms(pdb_path)
	if points.size == 0:
		return
	poly = pv.PolyData(points)
	poly["rgb"] = (colors * 255.0).astype(numpy.uint8)
	poly["radii"] = radii
	glyph = poly.glyph(scale="radii", geom=pv.Sphere(radius=1.0))
	plotter.add_mesh(
		glyph,
		scalars="rgb",
		rgb=True,
		lighting=True,
		smooth_shading=True,
		render_points_as_spheres=True,
	)


def _add_silhouette(plotter, pv, mesh, width=2):
	if width <= 0:
		return
	try:
		from pyvista import _vtk
	except Exception:
		return
	sil = _vtk.vtkPolyDataSilhouette()
	sil.SetInputData(mesh)
	sil.SetCamera(plotter.renderer.GetActiveCamera())
	sil.SetEnableFeatureAngle(True)
	sil.SetFeatureAngle(60.0)
	sil.Update()
	sil_poly = pv.wrap(sil.GetOutput())
	if sil_poly.n_points > 0:
		plotter.add_mesh(
			sil_poly,
			color="black",
			line_width=width,
			lighting=False,
			style="wireframe",
			reset_camera=False,
		)


def _setup_plotter(pv, imgsize):
	plotter = pv.Plotter(off_screen=True, window_size=(imgsize, imgsize))
	plotter.set_background("white")
	try:
		plotter.enable_lightkit()
	except Exception:
		pass
	try:
		plotter.add_light(pv.Light(position=(1, 1, 1), focal_point=(0, 0, 0), color="white"))
		plotter.add_light(pv.Light(position=(-1, -0.5, 0.8), focal_point=(0, 0, 0), color="white"))
	except Exception:
		pass
	try:
		plotter.enable_anti_aliasing("ssaa")
	except Exception:
		pass
	try:
		plotter.enable_eye_dome_lighting()
	except Exception:
		pass
	return plotter


def render_png_views(
	verts,
	faces,
	basename,
	imgsize=1024,
	cmap_name="viridis",
	pdb_path=None,
	silhouette_width=2,
	mesh_color="lightsteelblue",
):
	pv = _require_pyvista()
	mesh = _make_mesh(pv, verts, faces)
	out_base = Path(basename)
	views = [(0, 0, 1), (0, 90, 2), (90, 0, 3)]

	for elev, azim, idx in views:
		plotter = _setup_plotter(pv, imgsize)
		plotter.add_mesh(
			mesh,
			color=mesh_color,
			smooth_shading=True,
			ambient=0.3,
			diffuse=0.7,
			specular=0.2,
			specular_power=15.0,
		)
		_add_atoms(plotter, pv, pdb_path)
		plotter.camera_position = _camera_position(mesh, elev, azim)
		_add_silhouette(plotter, pv, mesh, width=silhouette_width)
		out_path = f"{out_base}.{idx}.png"
		plotter.show(auto_close=True, screenshot=out_path)


def render_animation_gif(
	verts,
	faces,
	basename,
	imgsize=512,
	n_frames=36,
	elev=30.0,
	pdb_path=None,
	silhouette_width=2,
	mesh_color="lightsteelblue",
):
	pv = _require_pyvista()
	mesh = _make_mesh(pv, verts, faces)
	out_base = Path(basename)
	tmp_dir = out_base.parent
	frames = []
	for i in range(n_frames):
		plotter = _setup_plotter(pv, imgsize)
		plotter.add_mesh(
			mesh,
			color=mesh_color,
			smooth_shading=True,
			ambient=0.3,
			diffuse=0.7,
			specular=0.2,
			specular_power=15.0,
		)
		_add_atoms(plotter, pv, pdb_path)
		azim = (360.0 / n_frames) * i
		plotter.camera_position = _camera_position(mesh, elev, azim)
		_add_silhouette(plotter, pv, mesh, width=silhouette_width)
		frame_path = tmp_dir / f"{out_base.name}.frame_{i:03d}.png"
		plotter.show(auto_close=True, screenshot=str(frame_path))
		try:
			with Image.open(frame_path) as frame:
				frames.append(frame.copy())
		finally:
			try:
				os.remove(frame_path)
			except OSError:
				pass

	if frames:
		out_gif = out_base.with_suffix(".animate.gif")
		frames[0].save(
			out_gif,
			save_all=True,
			append_images=frames[1:],
			duration=100,
			loop=0,
		)
	return Path(basename)
