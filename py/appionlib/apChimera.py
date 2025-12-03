###############
# Tools for using Chimera
###############

import os
import math
import time
import numpy
import random
import colorsys
from scipy import ndimage
from PIL import Image
#appion
from appionlib import apFile
from appionlib import apParam
from appionlib import apDisplay
from pyami import mrc
from appionlib import apVolumeRender

satvalue = 0.9
hsvalue = 0.5

def _normalize_volume(volume):
	std = volume.std()
	if std == 0:
		return volume
	return (volume - volume.mean()) / std

def _fermi_lowpass(volume, apix, cutoff, rolloff=0.1):
	if cutoff is None or cutoff <= 0:
		return volume
	vol = numpy.asarray(volume, dtype=numpy.float32)
	freq_z = numpy.fft.fftfreq(vol.shape[0], d=apix)
	freq_y = numpy.fft.fftfreq(vol.shape[1], d=apix)
	freq_x = numpy.fft.fftfreq(vol.shape[2], d=apix)
	fz, fy, fx = numpy.meshgrid(freq_z, freq_y, freq_x, indexing="ij")
	radius = numpy.sqrt(fx**2 + fy**2 + fz**2)
	cutoff_freq = 1.0 / float(cutoff)
	roll = max(cutoff_freq * rolloff, numpy.finfo(numpy.float32).eps)
	mask = 1.0 / (1.0 + numpy.exp((radius - cutoff_freq) / roll))
	filtered = numpy.fft.ifftn(numpy.fft.fftn(vol) * mask).real
	return filtered.astype(numpy.float32)

def _bilateral_filter_3d(vol, sigma_spatial=1.0, sigma_intensity=0.25, max_radius=2):
	"""
	Simple bilateral filter for 3D volumes using reflection padding.
	"""
	volume = numpy.asarray(vol, dtype=numpy.float32)
	radius = max(1, min(int(math.ceil(2 * sigma_spatial)), max_radius))
	coords = range(-radius, radius + 1)
	padded = numpy.pad(volume, radius, mode="reflect")
	accum = numpy.zeros_like(volume, dtype=numpy.float32)
	weights_sum = numpy.zeros_like(volume, dtype=numpy.float32)

	for dz in coords:
		for dy in coords:
			for dx in coords:
				spatial_sq = float(dx*dx + dy*dy + dz*dz)
				spatial_w = math.exp(-spatial_sq / (2.0 * sigma_spatial * sigma_spatial))
				z_slice = slice(radius + dz, radius + dz + volume.shape[0])
				y_slice = slice(radius + dy, radius + dy + volume.shape[1])
				x_slice = slice(radius + dx, radius + dx + volume.shape[2])
				shifted = padded[z_slice, y_slice, x_slice]
				intensity_w = numpy.exp(-((shifted - volume) ** 2) / (2.0 * sigma_intensity * sigma_intensity))
				w = spatial_w * intensity_w
				accum += w * shifted
				weights_sum += w

	weights_sum = numpy.maximum(weights_sum, numpy.finfo(numpy.float32).eps)
	return accum / weights_sum
#
#=========================================
#=========================================
def getSnapPath():
	chimsnappath = os.path.join(apParam.getAppionDirectory(), "appionlib", "apChimSnapshot.py")
	if not os.path.isfile(chimsnappath):
		libdir = os.path.dirname(__file__)
		chimsnappath = os.path.join(libdir, "apChimSnapshot.py")
	if not os.path.isfile(chimsnappath):
		apDisplay.printError("Could not find file: apChimSnapshot.py")
	return chimsnappath

#=========================================
#=========================================
def isValidVolume(volfile):
	"""
	Checks to see if a MRC volume is valid
	"""
	if not os.path.isfile(volfile):
		apDisplay.printWarning("volume path '%s' is not a file"%(volfile))
		return False
	volarray = mrc.read(volfile)
	if volarray.shape[0]*volarray.shape[1]*volarray.shape[2] > 400**3:
		apDisplay.printWarning("Volume is very large")
		return True
	if abs(volarray.min() - volarray.max()) < 1e-6:
		apDisplay.printWarning("Volume has zero standard deviation")
		return False
	return True

#=========================================
#=========================================
def setVolumeMass(volumefile, apix=1.0, mass=1.0, rna=0.0):
	"""
	Adjust the contour so the enclosed mass matches the requested kDa target.

	We assume a bulk density for protein/RNA (default 0.81 Da/Å^3 for protein,
	linearly adjusted toward 1.35 Da/Å^3 for RNA content). The routine finds
	the voxel threshold that yields the desired enclosed mass when multiplied
	by voxel volume.
	"""
	if isValidVolume(volumefile) is False:
		apDisplay.printError("Volume file %s is not valid"%(volumefile))
		return False
	if mass <= 0:
		apDisplay.printWarning("Mass must be positive; skipping mass-based scaling.")
		return False

	vol = mrc.read(volumefile).astype(numpy.float32)
	vol_for_threshold = vol.copy()
	# Binary/quantized maps need a bit of smoothing to expose usable thresholds.
	if numpy.unique(vol_for_threshold).size <= 4:
		vol_for_threshold = _bilateral_filter_3d(vol_for_threshold, sigma_spatial=1.0, sigma_intensity=0.25, max_radius=2)

	# Estimate density based on RNA fraction (very coarse model).
	protein_density = 0.81  # Da/Å^3
	rna_density = 1.35      # Da/Å^3
	rna_fraction = max(0.0, min(1.0, float(rna)))
	density_da_per_a3 = protein_density * (1 - rna_fraction) + rna_density * rna_fraction

	target_mass_da = mass * 1000.0
	voxel_volume = apix ** 3
	# Flatten and sort descending to walk from highest density down.
	flat = numpy.sort(vol_for_threshold.ravel())[::-1]
	cumulative_mass = numpy.cumsum(flat) * voxel_volume * density_da_per_a3

	threshold_index = numpy.searchsorted(cumulative_mass, target_mass_da)
	if threshold_index >= flat.size:
		apDisplay.printWarning("Target mass exceeds map integral; using minimum voxel value.")
		threshold_value = flat[-1]
	else:
		threshold_value = flat[threshold_index]

	# Normalize volume so contour 1.0 matches the threshold.
	scale = threshold_value if threshold_value != 0 else 1.0
	if scale == 0:
		apDisplay.printWarning("Computed threshold is zero; cannot scale.")
		return False
	vol_scaled = vol_for_threshold / scale
	mrc.write(vol_scaled, volumefile)
	apDisplay.printMsg("Mass-based scaling applied (target %.2f kDa, threshold %.5f)" % (mass, threshold_value))
	return True

#=========================================
#=========================================
def filterAndChimera(density, res=30, apix=None, box=None, chimtype='snapshot',
		contour=None, zoom=1.0, sym='c1', color=None, silhouette=True, mass=None):
	"""
	filter volume and then create a few snapshots for viewing on the web
	"""
	if isValidVolume(density) is False:
		apDisplay.printError("Volume file %s is not valid"%(density))
	if box is None:
		boxdims = apFile.getBoxSize(density)
		box = boxdims[0]
	### if eotest failed, filter to 30
	if not res or str(res) == 'nan':
		res = 30
	density = os.path.abspath(density)
	filtres = 0.6*res
	shrinkby = 1
	tmpf = os.path.abspath(density+'.tmp.mrc')
	cleanup_tmp = True
	apDisplay.printMsg("Low pass filtering model for images (Python)")
	vol = mrc.read(density).astype(numpy.float32)
	if box is not None and box > 250:
		shrinkby = int(math.ceil(box/160.0))
	filtered = _fermi_lowpass(vol, apix=apix, cutoff=filtres, rolloff=0.05)
	if shrinkby > 1:
		zoom = 1.0 / shrinkby
		filtered = ndimage.zoom(filtered, zoom=zoom, order=1)
	filtered = _normalize_volume(filtered)
	filtered[filtered < 0] = 0.0
	mrc.write(filtered, tmpf)
	del vol, filtered

	### render images
	renderSlice(density, box=box, tmpfile=tmpf, sym=sym)
	if chimtype != 'snapshot':
		renderAnimation(tmpf, contour, zoom, sym, color, silhouette, name=density)
	elif chimtype != 'animate':
		renderSnapshots(tmpf, contour, zoom, sym, color, silhouette, name=density)
	if cleanup_tmp:
		apFile.removeFile(tmpf)

#=========================================
#=========================================
def renderSlice(density, box=None, tmpfile=None, sym='c1'):
	"""
	create mrc of central slice for viruses
	"""
	if isValidVolume(density) is False:
		apDisplay.printError("Volume file is not valid")
	if tmpfile is None:
		tmpfile = density
	if box is None:
		boxdims = apFile.getBoxSize(tmpfile)
		box = boxdims[0]
	halfbox = int(box/2)
	vol = mrc.read(tmpfile)
	slice_idx = min(max(halfbox, 0), vol.shape[0]-1)
	slice_data = vol[slice_idx, :, :]
	minv = slice_data.min()
	maxv = slice_data.max()
	if maxv > minv:
		img_data = (255 * (slice_data - minv) / (maxv - minv)).astype(numpy.uint8)
	else:
		img_data = numpy.zeros_like(slice_data, dtype=numpy.uint8)
	pngslice = density + '.slice.png'
	Image.fromarray(img_data).save(pngslice)
	return pngslice

#=========================================
#=========================================
def renderSnapshots(density, contour=None, zoom=1.0, sym=None, color=None,
		silhouette=True, xvfb=False, pdb=None, name=None, print3d=False):
	"""
	create a few snapshots for viewing on the web (headless)
	"""
	if isValidVolume(density) is False:
		apDisplay.printError("Volume file is not valid")
	if name is not None:
		basename = name
	else:
		basename = os.path.splitext(density)[0]
	vol = mrc.read(density).astype(numpy.float32)
	verts, faces = apVolumeRender.extract_mesh(vol, level=contour, spacing=(1.0, 1.0, 1.0))
	apVolumeRender.render_png_views(verts, faces, basename, imgsize=512)
	if print3d:
		apVolumeRender.export_stl(verts, faces, basename + ".stl")
	return basename

#=========================================
#=========================================
def renderAnimation(density, contour=None, zoom=1.0, sym=None, color=None,
		silhouette=False, xvfb=False, name=None):
	"""
	create several snapshots and merge into animated GIF (headless)
	"""
	if isValidVolume(density) is False:
		apDisplay.printError("Volume file is not valid")
	basename = name or density
	vol = mrc.read(density).astype(numpy.float32)
	verts, faces = apVolumeRender.extract_mesh(vol, level=contour, spacing=(1.0, 1.0, 1.0))
	apVolumeRender.render_animation_gif(verts, faces, basename, imgsize=512)
	return basename

#=========================================
#=========================================
def runChimeraScript(chimscript, xvfb=False):
	apDisplay.printError("Chimera rendering path removed; use renderSnapshots/renderAnimation (headless) instead.")

#=========================================
#=========================================
def colorToString(color):
	color = color.lower()
	apDisplay.printMsg("selecting color: "+color)
	### primary colors
	if color == "red":
		apDisplay.printColor("using color RED", "red")
		return "0.71:0.06:0.00,None,0.71:0.06:0.00"
	if color == "orange":
		apDisplay.printColor("using color ORANGE", "orange")
		return "0.90:0.57:0.00,None,0.94:0.57:0.00"
	if color == "yellow":
		apDisplay.printColor("using color YELLOW", "yellow")
		return "0.99:0.89:0.00,None,0.95:0.95:0.00"
	if color == "green":
		apDisplay.printColor("using color GREEN", "green")
		return "0.28:0.59:0.00,None,0.28:0.59:0.00"
	if color == "blue":
		apDisplay.printColor("using color BLUE", "blue")
		return "0.00:0.21:0.75,None,0.00:0.21:0.75"
	if color == "violet":
		apDisplay.printColor("using color VIOLET", "violet")
		return "0.39:0.00:0.51,None,0.39:0.00:0.51"
	### seconary colors
	if color == "red-orange":
		apDisplay.printColor("using color RED_ORANGE", "red")
		return "0.91:0.28:0.00,None,0.91:0.28:0.00"
	if color == "yellow-orange" or color == "gold":
		apDisplay.printColor("using color GOLD", "yellow")
		return "0.94:0.70:0.00,None,0.94:0.70:0.00"
	if color == "yellow-green" or color == "limegreen":
		apDisplay.printColor("using color LIMEGREEN", "yellow")
		return "0.65:0.74:0.07,None,0.65:0.74:0.07"
	if color == "blue-green" or color == "cyan":
		apDisplay.printColor("using color CYAN", "cyan")
		return "0.00:0.54:0.77,None,0.00:0.54:0.77"
	if color == "blue-violet" or color == "purple":
		apDisplay.printColor("using color PURPLE", "violet")
		return "0.18:0.00:0.48,None,0.18:0.00:0.48"
	if color == "red-violet" or color == "maroon" or color == "magenta":
		apDisplay.printColor("using color MAROON", "magenta")
		return "0.49:0.07:0.22,None,0.49:0.07:0.22"
	### boring colors
	if color == "black":
		apDisplay.printColor("using color BLACK", "white")
		return "0.2:0.2:0.2,None,0.2:0.2:0.2"
	if color == "gray":
		apDisplay.printColor("using color GRAY", "white")
		return "0.6:0.6:0.6,None,0.6:0.6:0.6"
	return "None,None,None"

#=========================================
#=========================================
def getColorString():
	#return secondColor()+",None,"+minuteColor()
	first = hourColor()
	#print "first", first
	third = minuteColor()
	#third = secondColor()
	#print "third", third
	colortuple = first+",None,"+third
	#print colortuple
	return colortuple

#=========================================
#=========================================
def dayColor():
	hue = ((time.time()/(24*3600.))%365)/365
	rgbindex = colorsys.hsv_to_rgb(hue, satvalue, hsvalue)
	colorstr = "%.1f:%.1f:%.1f"%(rgbindex[0], rgbindex[1], rgbindex[2])
	return colorstr

#=========================================
#=========================================
def hourColor():
	hue = ((time.time()/3600.)%24)/24
	rgbindex = colorsys.hsv_to_rgb(hue, satvalue, hsvalue)
	colorstr = "%.1f:%.1f:%.1f"%(rgbindex[0], rgbindex[1], rgbindex[2])
	return colorstr

#=========================================
#=========================================
def minuteColor():
	hue = ((time.time()/60.)%60)/60
	rgbindex = colorsys.hsv_to_rgb(hue, satvalue, hsvalue)
	colorstr = "%.1f:%.1f:%.1f"%(rgbindex[0], rgbindex[1], rgbindex[2])
	return colorstr

#=========================================
#=========================================
def secondColor():
	hue = ((time.time()/10.)%60)/60
	rgbindex = colorsys.hsv_to_rgb(hue, satvalue, hsvalue)
	colorstr = "%.1f:%.1f:%.1f"%(rgbindex[0], rgbindex[1], rgbindex[2])
	return colorstr

#=========================================
#=========================================
def randomColor():
	hue = random.random()
	rgbindex = colorsys.hsv_to_rgb(hue, satvalue, hsvalue)
	colorstr = "%.1f:%.1f:%.1f"%(rgbindex[0], rgbindex[1], rgbindex[2])
	return colorstr

#=========================================
#=========================================
def isTooGray(rgbindex):
	mindiff = 0.16
	d1 = abs(rgbindex[0]-rgbindex[1])
	d2 = abs(rgbindex[0]-rgbindex[2])
	d3 = abs(rgbindex[1]-rgbindex[2])
	if d1 < mindiff and d2 < mindiff and d3 < mindiff:
		return True
	return False

#=========================================
#=========================================
def isTooLight(rgbindex):
	maxsum = 0.67
	csum = rgbindex[0]+rgbindex[1]+rgbindex[2]
	if csum > maxsum:
		return True
	return False

#=========================================
#=========================================
def isGoodColor(rgbindex):
	if isTooGray(rgbindex):
		# color is too gray
		return False
	if isTooLight(rgbindex):
		# color is too light-colored
		return False
	return True

#=========================================
#=========================================
def getColorList():
	colorlist = []
	for i in range(216):
		rgbindex = [ i%6, (i/6)%6, (i/36)%6 ]
		if isGoodColor(rgbindex):
			colorlist.append(rgbindex)
