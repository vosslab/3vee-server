#!/usr/bin/env python3
"""
Volume binning helpers (3D).

These mirror the legacy `bin3` helpers from the upstream pyami tree but avoid
any external dependencies beyond NumPy.
"""

import numpy


def _trim_to_factor(a, factor):
	"""
	Trim a 3D array so each dimension is divisible by factor.
	"""
	z, y, x = a.shape
	new_z = (z // factor) * factor
	new_y = (y // factor) * factor
	new_x = (x // factor) * factor
	return a[:new_z, :new_y, :new_x]


def bin3(a, factor):
	"""
	Bin a 3D array in real space by an integer factor using mean aggregation.

	Any remainder voxels (when a.shape is not divisible by factor) are dropped.
	"""
	if factor <= 0:
		raise ValueError("factor must be a positive integer")
	if a.ndim != 3:
		raise ValueError("bin3 expects a 3D array")

	trimmed = _trim_to_factor(numpy.asarray(a), factor)
	newshape = (trimmed.shape[0] // factor,
	            factor,
	            trimmed.shape[1] // factor,
	            factor,
	            trimmed.shape[2] // factor,
	            factor)
	reshaped = numpy.reshape(trimmed, newshape)
	binned = reshaped.mean(axis=(1, 3, 5))
	return binned


def bin3f(a, factor):
	"""
	Bin a 3D array in Fourier space by cropping the spectrum.

	This keeps the low-frequency cube and rescales by factor^3 to preserve
	intensity.
	"""
	if factor <= 0:
		raise ValueError("factor must be a positive integer")
	if a.ndim != 3:
		raise ValueError("bin3f expects a 3D array")

	fft = numpy.fft.fftn(a)
	fft = numpy.fft.fftshift(fft)

	def _bounds(length):
		start = int(length / 2 * (1 - (1.0 / factor)))
		end = int(length / 2 * (1 + (1.0 / factor)))
		return start, end

	zstart, zend = _bounds(fft.shape[0])
	ystart, yend = _bounds(fft.shape[1])
	xstart, xend = _bounds(fft.shape[2])

	cropped = fft[zstart:zend, ystart:yend, xstart:xend]
	cropped = numpy.fft.fftshift(cropped)
	binned = numpy.fft.ifftn(cropped) / float(factor ** 3)
	return binned.real
