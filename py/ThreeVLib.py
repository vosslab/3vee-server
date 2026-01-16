
"""
Python library for running 3v programs
"""

import os
import re
import sys
import time
import glob
import math
import numpy
import random
import shutil
import locale
import subprocess
import shlex
from scipy import ndimage
from string import ascii_lowercase
#local
from appionlib import apDisplay
from appionlib import apParam
from appionlib import apHeadlessRender
from appionlib import apFile
from pyami import mrc, surfarea

class ThreeVLib(object):
	#====================
	def __init__(self, jobid=None):
		os.umask(000)
		self.waited = 0
		if jobid is not None:
			self.jobid = jobid
		else:
			datestamp = time.strftime("%y%b%d").lower()
			randstamp = "".join(random.choice(ascii_lowercase) for _ in range(3))
			self.jobid = datestamp+"."+randstamp
		#self.rundir = "."
		self.procdir = "/var/www/html/3vee"
		base_url = os.environ.get("THREEV_BASE_URL", "http://localhost:8080")
		self.web_base = base_url.rstrip("/")
		self.output_url = self.web_base + "/output"
		self.datestamp = self.jobid[:7]
		self.jobdir = re.sub(r'\.', '/', self.jobid)
		self.rundir = os.path.join(self.procdir, "output", self.jobdir)
		if not os.path.isdir(self.rundir):
			os.mkdir(self.rundir)
		os.chdir(self.rundir)
		self.runlogfile = os.path.join(self.procdir, "output", self.jobdir ,"runlog-"+self.jobid+".html")
		self.pdbid = None

	@staticmethod
	def _normalize_volume(volume):
		"""
		Shift mean to 0 and scale to unit standard deviation (legacy norm=0,1 behavior).
		"""
		std = volume.std()
		if std == 0:
			return volume
		return (volume - volume.mean()) / std

	@staticmethod
	def _fermi_lowpass(volume, apix, cutoff, rolloff=0.1):
		"""
		Apply a smooth low-pass filter in Fourier space using a Fermi-style mask.
		cutoff is in angstroms (legacy tlp/lp convention); rolloff is
		expressed as a fraction of the cutoff frequency.
		"""
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

	#====================
	def runCommand(self, cmd, verbose=False, showcmd=True, source=True):
		self.checkSystemLoad()
		"""
		executes an shell command in a controlled fashion
		"""
		#self.writeToRunningLog("running command: "+cmd, "Star")
		waited = False
		if showcmd is True:
			sys.stderr.write(apDisplay.colorString("COMMAND: ","magenta")+cmd+"\n")
		t0 = time.time()
		popen_kwargs = {}
		popen_kwargs = {}
		if source is True:
			cmd = "source /etc/bashrc; "+cmd
			popen_kwargs["executable"] = "/bin/bash"
			popen_kwargs["env"] = os.environ.copy()
			popen_kwargs["env"]["BASH_ENV"] = "/etc/bashrc"
		try:
			if verbose is False:
				proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **popen_kwargs)
			else:
				proc = subprocess.Popen(cmd, shell=True, **popen_kwargs)
			if verbose is True:
				proc.wait()
			else:
				### continuous check
				waittime = 2.0
				while proc.poll() is None:
					if waittime > 10:
						waited = True
						sys.stderr.write(".")
					waittime *= 1.1
					time.sleep(waittime)
		except:
			self.writeToRunningLog("could not run command: "+cmd, "Cross")
			raise
		tdiff = time.time() - t0
		if tdiff > 20:
			apDisplay.printMsg("completed in "+apDisplay.timeString(tdiff))
		elif waited is True:
			print("")

	#====================
	def checkSystemLoad(self):
		waitnow = False
		maxload = 2.0
		loads = os.getloadavg()
		while loads[0] > maxload:
			waittime = (loads[0]-1.0)**3+0.1
			waitnow = True
			self.waited += waittime
			timestr = apDisplay.timeString(self.waited)
			self.writeToRunningLog(("waiting for system load (%.2f) to calm down, total wait time: %s"%
				(loads[0], timestr)), type="Star")
			time.sleep(waittime)
			loads = os.getloadavg()
			maxload += 0.5
		if waitnow is True:
			self.writeToRunningLog("running now")

	#====================
	def fileSize(self, fname):
		if not os.path.isfile(fname):
			return None
		size = os.stat(fname)[6]/1024.0
		return int(round(size))

	#====================
	def getNumLines(self, fname):
		f = open(fname, "r")
		numlines = len(f.readlines())
		f.close()
		return numlines

	#====================
	def downloadPDB(self, pdbid, biounit=False):
		self.pdbid = pdbid
		self.checkSystemLoad()
		self.writeToRunningLog("downloading pdb file")
		pdbfile = os.path.join(self.rundir, pdbid+"-"+self.jobid+".pdb")

		### download the file
		if os.path.isfile(pdbfile+".gz"):
			os.remove(pdbfile+".gz")
		rcsb_base = "https://files.rcsb.org/download/%s"%(pdbid.upper())
		if biounit is True:
			self.pdburl = rcsb_base + ".pdb1.gz"
		else:
			self.pdburl = rcsb_base + ".pdb.gz"
		wgetcmd = "wget '"+self.pdburl+"' -O "+pdbfile+".gz"
		self.runCommand(wgetcmd, verbose=True)
		if not os.path.isfile(pdbfile+".gz") or self.fileSize(pdbfile+".gz") < 10:
			self.writeToRunningLog("failed to download pdb id: "+pdbid, type="Cross")
			if biounit is False:
				sys.exit(1)
			self.runCommand("rm -f "+pdbfile+".gz", verbose=False)
			self.writeToRunningLog("trying download pdb id again without bio unit")
			self.pdburl = rcsb_base + ".pdb.gz"
			wgetcmd = "wget '"+self.pdburl+"' -O "+pdbfile+".gz"
			self.runCommand(wgetcmd, verbose=True)
			if not os.path.isfile(pdbfile+".gz") or self.fileSize(pdbfile+".gz") < 10:
				self.writeToRunningLog("failed to download pdb id again: "+pdbid, type="Cross")
				sys.exit(1)

		### unzip the file
		if os.path.isfile(pdbfile):
			os.remove(pdbfile)
		gzcmd = "gunzip "+pdbfile+".gz"
		self.runCommand(gzcmd, verbose=True)
		if not os.path.isfile(pdbfile):
			self.writeToRunningLog("failed to download pdb id: "+pdbid, type="Cross")
			sys.exit(1)
		size = self.fileSize(pdbfile)
		numlines = self.getNumLines(pdbfile)
		self.writeToRunningLog("completed download of PDB id"
			+(" %s (size: %d k, %d lines)"%(pdbid,size,numlines)))
		return pdbfile
		
	#====================
	def convertPDBtoXYZR(self, pdbfile, hetero=False):
		self.checkSystemLoad()
		self.writeToRunningLog("converting pdb into xyzr")
		### remove atoms
		atomfile = os.path.splitext(os.path.basename(pdbfile))[0]+".atoms"
		inf = open(pdbfile, "r")
		outf = open(atomfile, "w")
		for line in inf:
			if line[:6] == "ATOM  ":
				outf.write(line)
			elif hetero and line[:6] == "HETATM":
				outf.write(line)
		inf.close()
		outf.close()

		if not os.path.isfile(atomfile):
			self.writeToRunningLog("failed to find any atoms in pdb file, no result", type="Cross")
			sys.exit(1)

		### convert file
		atmftypeile = os.path.join(self.procdir, "dat/atmtypenumbers.dat")
		if not os.path.isfile(atmftypeile):
			apDisplay.printError("could not find file: "+atmftypeile)
		shutil.copy(atmftypeile, self.rundir)
		newatm = os.path.join(self.rundir, "atmtypenumbers.dat")
		if not os.path.isfile(newatm):
			apDisplay.printError("could not find file: "+newatm)
		xyzrfile = os.path.splitext(pdbfile)[0]+".xyzr"

		convertexe = os.path.join(self.procdir, "bin/pdb_to_xyzr.exe") 
		convertcmd = convertexe+" "+atomfile+" > "+xyzrfile
		print(os.getcwd())
		os.chdir(self.rundir)
		self.runCommand(convertcmd, verbose=True)

		anumlines = self.getNumLines(atomfile)

		### remove files
		os.remove(os.path.basename(atmftypeile))
		os.remove(os.path.basename(atomfile))
		#os.remove(os.path.basename(pdbfile))
		#gzcmd = "gzip -9 "+pdbfile
		#self.runCommand(gzcmd, verbose=True)

		### check results
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to convert pdb file, no result", type="Cross")
			sys.exit(1)
		size = self.fileSize(xyzrfile)
		xnumlines = self.getNumLines(xyzrfile)
		self.writeToRunningLog("completed conversion of PDB file: "
			+os.path.basename(pdbfile)+" (size: "+str(size)+"k)")
		self.writeToRunningLog("converted %d atoms of %d atoms"%(xnumlines,anumlines) )
		if xnumlines < 1:  #or size < 1:
			self.writeToRunningLog("failed to convert pdb file, no atoms found", type="Cross")
			sys.exit(1)

		self.writeToRunningLog("found %d atoms in pdb"%(xnumlines))
		return xyzrfile

	#====================
	def convertCCP4toMRC(self, ccp4file, mrcfile=None):
		self.checkSystemLoad()
		self.writeToRunningLog("converting ccp4 into mrc")
		if mrcfile is None:
			mrcfile = os.path.splitext(ccp4file)[0]+".mrc"
		if os.path.isfile(mrcfile):
			os.remove(mrcfile)

		try:
			volume = mrc.read(ccp4file)
		except Exception:
			self.writeToRunningLog("failed to read CCP4 file for conversion", type="Cross")
			raise

		header = mrc.getHeader(volume)
		mrc.write(volume, mrcfile, header=header)

		if not os.path.isfile(mrcfile):
			self.writeToRunningLog("failed to convert CCP4 to MRC", type="Cross")
			sys.exit(1)

		return mrcfile

	#====================
	def runFsvCalc(self, xyzrfile, bigprobe=6.0, smallprobe=2.0, trimprobe=1.5, gridsize=0.5, mrcfile=None):
		self.checkSystemLoad()
		"""
		./FsvCalc.exe -i <file> -b <big_probe> -s <small_probe> 
			-t <trim probe> -m <MRC outfile> -g <gridspace>
		FsvCalc.exe -- Calculates the Fractional Solvent Volume
		"""
		self.writeToRunningLog("running 3v fsv calc program")
		if mrcfile is None:
			mrcfile = os.path.splitext(xyzrfile)[0]+".mrc"

		fsvcalccmd  = os.path.join(self.procdir, "bin/FsvCalc.exe")
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to find XYZR file to run FSVCalc.exe", type="Cross")
			sys.exit(1)
		fsvcalccmd += " -i %s"%(xyzrfile)
		fsvcalccmd += " -b %.3f"%(bigprobe)
		fsvcalccmd += " -s %.3f"%(smallprobe)
		fsvcalccmd += " -t %.3f"%(trimprobe)
		fsvcalccmd += " -g %.3f"%(gridsize)
		fsvcalccmd += " -m %s"%(mrcfile)
		self.runCommand(fsvcalccmd, verbose=True)

		logfile = os.path.join(self.rundir, "shell-"+self.jobid+".log")
		f = open(logfile, "r")
		fsvdata = {}
		fsvdata['mrcfile'] = mrcfile
		ezdfile = os.path.splitext(mrcfile)[0] + ".ezd"
		if os.path.isfile(ezdfile):
			fsvdata['ezdfile'] = ezdfile
		for line in f:
			if line[:26] == "FRACTIONAL SOLVENT VOLUME:":
				bits = line.strip().split(":")
				if len(bits) < 2:
					self.writeToRunningLog("failed to get result from FSVCalc.exe", type="Cross")
					sys.exit(1)
				percent = bits[1].strip()
				fsvdata['fsv'] = float(re.sub("%","", percent))
		if re.match(r"SOLVENT \(R = [0-9\.]+\) VOLUME:",line):
				bits = line.strip().split(":")
				if len(bits) < 2:
					self.writeToRunningLog("failed to get result from FSVCalc.exe", type="Cross")
					sys.exit(1)
				fsvdata['solventvol'] = float(bits[1].strip())
		if re.match(r"BIG PROBE \(R = [0-9\.]+\) VOLUME:",line):
				bits = line.strip().split(":")
				if len(bits) < 2:
					self.writeToRunningLog("failed to get result from FSVCalc.exe", type="Cross")
					sys.exit(1)
				fsvdata['shellvol'] = float(bits[1].strip())
		if re.match(r"TRIMMED \(BY R = [0-9\.]+\) VOLUME:",line):
				bits = line.strip().split(":")
				if len(bits) < 2:
					self.writeToRunningLog("failed to get result from FSVCalc.exe", type="Cross")
					sys.exit(1)
				fsvdata['trimvol'] = float(bits[1].strip())
		f.close()
		if fsvdata['fsv'] is None:
			self.writeToRunningLog("failed to get result from FSVCalc.exe", type="Cross")
			sys.exit(1)

		return fsvdata

	#====================
	def runChannel(self, xyzrfile, bigprobe=6.0, smallprobe=2.0, trimprobe=1.5, 
		xyzcoord=(None,None,None), gridsize=0.5, mrcfile=None):
		self.checkSystemLoad()
		"""
		./Channel.exe -i <file> -b <big_probe> -s <small_probe> 
			-t <trim probe> -x <x-coord> -y <y-coord> -z <z-coord>
			-m <MRC outfile> -g <gridspace>
		Channel.exe -- Extracts a particular channel from the solvent
		"""
		self.writeToRunningLog("running 3v channel program")
		if mrcfile is None:
			mrcfile = os.path.splitext(xyzrfile)[0]+".mrc"

		channelcmd  = os.path.join(self.procdir, "bin/Channel.exe")
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to find XYZR file to run Channel.exe", type="Cross")
			sys.exit(1)
		channelcmd += " -i %s"%(xyzrfile)
		channelcmd += " -b %.3f"%(bigprobe)
		channelcmd += " -s %.3f"%(smallprobe)
		channelcmd += " -t %.3f"%(trimprobe)
		channelcmd += " -g %.3f"%(gridsize)
		channelcmd += " -m %s"%(mrcfile)
		if self.script.params['waterpdb'] is True:
			pdbfile = re.sub(".mrc", ".pdb", mrcfile)
			channelcmd += " -o %s"%(pdbfile)
		self.runCommand(channelcmd, verbose=True)

		if os.path.isfile(mrcfile):
			print("wrote to file: "+mrcfile)
			return mrcfile
		else:
			self.writeToRunningLog("failed to create an MRC file", type="Cross")
			sys.exit(1)

	#====================
	def runChannelFinder(self, xyzrfile, bigprobe=6.0, smallprobe=2.0, trimprobe=1.5, 
		gridsize=0.5, mrcfile=None, minvolume=None, minpercent=None, numchan=None):
		self.checkSystemLoad()
		"""
		./AllChannel.exe -i <file> -b <big_probe> -s <small_probe> -g <gridspace> 
			-t <trim probe> -v <min-volume in A^3> -p <min-percent>
		AllChannel.exe -- Extracts all channels from the solvent above a cutoff
		"""
		self.writeToRunningLog("running 3v all channel program")
		if mrcfile is None:
			mrcfile = os.path.splitext(xyzrfile)[0]+".mrc"
		mrcfile = os.path.abspath(mrcfile)

		chanfindcmd  = os.path.join(self.procdir, "bin/AllChannel.exe")
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to find XYZR file to run AllChannel.exe", type="Cross")
			sys.exit(1)
		chanfindcmd += " -i %s"%(xyzrfile)
		chanfindcmd += " -b %.3f"%(bigprobe)
		chanfindcmd += " -s %.3f"%(smallprobe)
		chanfindcmd += " -t %.3f"%(trimprobe)
		chanfindcmd += " -g %.3f"%(gridsize)
		if numchan is not None:
			chanfindcmd += " -n %d"%(numchan)
		elif minvolume is not None:
			chanfindcmd += " -v %d"%(minvolume)
		elif minpercent is not None:
			chanfindcmd += " -p %.6f"%(minpercent)
		else:
			chanfindcmd += " -p %.6f"%(0.001)
		chanfindcmd += " -m %s"%(mrcfile)

		self.runCommand(chanfindcmd, verbose=True)

		mrcfiles = glob.glob(os.path.join(os.path.dirname(mrcfile), "*.mrc"))
		if len(mrcfiles) > 0:
			self.writeToRunningLog("created %d channel files"%(len(mrcfiles)))
			text = ""
			count = 1
			for mrcfile in mrcfiles:
				link = re.sub("/var/www/html/3vee/output", self.output_url, mrcfile)
				text += "<a href='%s'>%d</a> \n"%(link, count)
				count += 1
			self.writeToRunningLog("Download MRC files: "+text)
			return mrcfiles
		else:
			self.writeToRunningLog("failed to find any channels, reduce the volume cutoff", type="Cross")
			sys.exit(1)

	#====================
	def runTunnel(self, xyzrfile, bigprobe=6.0, smallprobe=2.0, trimprobe=1.5, 
		gridsize=0.5, mrcfile=None):
		self.checkSystemLoad()
		"""
		./Tunnel.exe -i <file> -g <grid spacing> -p <tunnel probe radius>
			-e <EZD outfile> -o <PDB outfile> -m <MRC outfile>
			-s <shell radius> -t <trim radius>
		Tunnel.exe -- Extracts the ribosomal exit tunnel from the H. marismortui structure
		"""
		self.writeToRunningLog("running 3v exit tunnel program")
		if mrcfile is None:
			mrcfile = os.path.splitext(xyzrfile)[0]+".mrc"

		tunnelcmd  = os.path.join(self.procdir, "bin/Tunnel.exe")
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to find XYZR file to run Tunnel.exe", type="Cross")
			sys.exit(1)
		tunnelcmd += " -i %s"%(xyzrfile)
		tunnelcmd += " -b %.3f"%(bigprobe)
		tunnelcmd += " -s %.3f"%(smallprobe)
		tunnelcmd += " -t %.3f"%(trimprobe)
		tunnelcmd += " -g %.3f"%(gridsize)
		tunnelcmd += " -m %s"%(mrcfile)
		if self.script.params['waterpdb'] is True:
			pdbfile = re.sub(".mrc", ".pdb", mrcfile)
			tunnelcmd += " -o %s"%(pdbfile)
		self.runCommand(tunnelcmd, verbose=True)

		if os.path.isfile(mrcfile):
			print("wrote to file: "+mrcfile)
			return mrcfile
		else:
			self.writeToRunningLog("failed to create an MRC file", type="Cross")
			sys.exit(1)

	#====================
	def runSolvent(self, xyzrfile, bigprobe=6.0, smallprobe=2.0, trimprobe=1.5, 
		gridsize=0.5, mrcfile=None):
		self.checkSystemLoad()
		"""
		./Solvent.exe -i <file> -s <sm_probe_rad> -b <big_probe_rad>
			-t <trim_probe_rad> -g <grid spacing> 
			-e <EZD outfile> -o <PDB outfile> -m <MRC outfile>
		Solvent.exe -- Extracts the all of the solvent
		"""
		self.writeToRunningLog("running 3v solvent program")
		if mrcfile is None:
			mrcfile = os.path.splitext(xyzrfile)[0]+".mrc"

		channelcmd  = os.path.join(self.procdir, "bin/Solvent.exe")
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to find XYZR file to run Solvent.exe", type="Cross")
			sys.exit(1)
		channelcmd += " -i %s"%(xyzrfile)
		channelcmd += " -b %.3f"%(bigprobe)
		channelcmd += " -s %.3f"%(smallprobe)
		channelcmd += " -t %.3f"%(trimprobe)
		channelcmd += " -g %.3f"%(gridsize)
		channelcmd += " -m %s"%(mrcfile)
		if self.script.params['waterpdb'] is True:
			pdbfile = re.sub(".mrc", ".pdb", mrcfile)
			channelcmd += " -o %s"%(pdbfile)
		self.runCommand(channelcmd, verbose=True)

		if os.path.isfile(mrcfile):
			print("wrote to file: "+mrcfile)
			return mrcfile
		else:
			self.writeToRunningLog("failed to create an MRC file", type="Cross")
			sys.exit(1)

	#====================
	def runCavity(self, xyzrfile, bigprobe=6.0, smallprobe=2.0, trimprobe=1.5, 
		xyzcoord=(0.0,0.0,0.0), gridsize=0.5, mrcfile=None):
		self.checkSystemLoad()
		"""
		./Channel.exe -i <file> -b <big_probe> -s <small_probe> 
			-t <trim probe> -x <x-coord> -y <y-coord> -z <z-coord>
			-m <MRC outfile> -g <gridspace>
		Channel.exe -- Extracts a particular channel from the solvent
		"""
		self.writeToRunningLog("running 3v channel program")
		if mrcfile is None:
			mrcfile = os.path.splitext(xyzrfile)[0]+".mrc"

		channelcmd  = os.path.join(self.procdir, "bin/Channel.exe")
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to find XYZR file to run Channel.exe", type="Cross")
			sys.exit(1)
		channelcmd += " -i %s"%(xyzrfile)
		channelcmd += " -b %.3f"%(bigprobe)
		channelcmd += " -s %.3f"%(smallprobe)
		channelcmd += " -t %.3f"%(trimprobe)
		channelcmd += " -g %.3f"%(gridsize)
		if all(coord is not None for coord in xyzcoord):
			channelcmd += " -x %.3f"%(xyzcoord[0])
			channelcmd += " -y %.3f"%(xyzcoord[1])
			channelcmd += " -z %.3f"%(xyzcoord[2])
		channelcmd += " -m %s"%(mrcfile)
		if self.script.params['waterpdb'] is True:
			pdbfile = re.sub(".mrc", ".pdb", mrcfile)
			channelcmd += " -o %s"%(pdbfile)
		self.runCommand(channelcmd, verbose=True)

		if os.path.isfile(mrcfile):
			print("wrote to file: "+mrcfile)
			return mrcfile
		else:
			self.writeToRunningLog("failed to create an MRC file", type="Cross")
			sys.exit(1)


	#====================
	def runVolume(self, xyzrfile, probe=3.0, gridsize=0.5, mrcfile=None):
		self.checkSystemLoad()
		"""
		./Volume.exe -i <file> -g <gridspacing> -p <probe_rad> 
			-m <MRC outfile> -o <PDB outfile> -m <MRC outfile>
		Volume.exe -- Calculate the volume and surface area for any probe radius
		"""
		self.writeToRunningLog("running 3v volume program")
		if mrcfile is None:
			mrcfile = os.path.splitext(xyzrfile)[0]+".mrc"


		volumecmd  = os.path.join(self.procdir, "bin/Volume.exe")
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to find XYZR file to run Volume.exe", type="Cross")
			sys.exit(1)
		volumecmd += " -i %s"%(xyzrfile)
		volumecmd += " -p %.3f"%(probe)
		volumecmd += " -g %.3f"%(gridsize)
		volumecmd += " -m %s"%(mrcfile)
		if self.script.params['waterpdb'] is True:
			pdbfile = re.sub(".mrc", ".pdb", mrcfile)
			volumecmd += " -o %s"%(pdbfile)
		self.runCommand(volumecmd, verbose=True)

		if os.path.isfile(mrcfile):
			print("wrote to mrc file: "+mrcfile)
			return mrcfile
		else:
			self.writeToRunningLog("unknown output for Volume.exe", type="Cross")
			sys.exit(1)

	#====================
	def runVolumeNoCav(self, xyzrfile, probe=3.0, gridsize=0.5, mrcfile=None):
		self.checkSystemLoad()
		"""
		./VolumeNoCav.exe -i <file> -g <gridspacing> -p <probe_rad> 
			-m <MRC outfile> -o <PDB outfile> -m <MRC outfile>
		VolumeNoCav.exe -- Calculate the volume and surface area for any probe radius
		"""
		self.writeToRunningLog("running 3v volume program")
		if mrcfile is None:
			mrcfile = os.path.splitext(xyzrfile)[0]+".mrc"

		volumecmd  = os.path.join(self.procdir, "bin/VolumeNoCav.exe")
		if not os.path.isfile(xyzrfile):
			self.writeToRunningLog("failed to find XYZR file to run VolumeNoCav.exe", type="Cross")
			sys.exit(1)
		volumecmd += " -i %s"%(xyzrfile)
		volumecmd += " -p %.3f"%(probe)
		volumecmd += " -g %.3f"%(gridsize)
		volumecmd += " -m %s"%(mrcfile)
		self.runCommand(volumecmd, verbose=True)

		if os.path.isfile(mrcfile):
			print("wrote to mrc file: "+mrcfile)
			return mrcfile
		else:
			self.writeToRunningLog("unknown output for VolumeNoCav.exe", type="Cross")
			sys.exit(1)

	#====================
	def trimMrcFile(self, mrcfile, flataxis=None, trimpercent=-1):
		self.checkSystemLoad()		
		self.writeToRunningLog("trimming mrc volume")

		if not os.path.isfile(mrcfile):
			self.writeToRunningLog("failed to find MRC file to run mrcTrim.py", type="Cross")
			sys.exit(1)

		volumecmd  = os.path.join(self.procdir, "py/mrcTrim.py")
		volumecmd += " -f "+mrcfile
		if trimpercent is not None:
			volumecmd += " -p %.4f"%(trimpercent)
			self.writeToRunningLog("custom trim percent %d"%(trimpercent*100))
		elif flataxis is not None and flataxis != "auto":
			volumecmd += " -p -1.0"
		if flataxis is not None and flataxis != "auto":
			self.writeToRunningLog("custom axis %s"%(flataxis))
			volumecmd += " -a "+flataxis

		self.runCommand(volumecmd, verbose=True)

		rootname = os.path.splitext(mrcfile)[0]
		trimMrcFile = rootname+"-trim.mrc"
		if not os.path.isfile(trimMrcFile):
			self.writeToRunningLog("FAILED to trim MRC file: "+trimMrcFile, type="Cross")
			return None
		self.writeToRunningLog("trimmed MRC file: "+trimMrcFile, type="Check")
		return trimMrcFile

	#====================
	def bisectMrcFile(self, mrcfile, flataxis=None):
		self.checkSystemLoad()		
		self.writeToRunningLog("trimming mrc volume")

		if not os.path.isfile(mrcfile):
			self.writeToRunningLog("failed to find MRC file to run mrcTrim.py", type="Cross")
			sys.exit(1)

		volumecmd  = os.path.join(self.procdir, "py/mrcBisect.py")
		volumecmd += " -f "+mrcfile
		if flataxis is not None and flataxis != "auto":
			self.writeToRunningLog("custom axis %s"%(flataxis))
			volumecmd += " -a "+flataxis

		self.runCommand(volumecmd, verbose=True)

		rootname = os.path.splitext(mrcfile)[0]
		bisectMrcFile1 = rootname+"-top.mrc"
		bisectMrcFile2 = rootname+"-bot.mrc"

		if not os.path.isfile(bisectMrcFile1):
			self.writeToRunningLog("FAILED to bisect MRC file: "+bisectMrcFile1, type="Cross")
			return None
		self.writeToRunningLog("bisected MRC file: "+bisectMrcFile1, type="Check")
		return bisectMrcFile1, bisectMrcFile2

	#====================
	def meshlabDecimateConvert(self, xthreedfile):
		t0 = time.time()
		self.checkSystemLoad()		

		if not os.path.isfile(xthreedfile):
			self.writeToRunningLog("failed to find X3D file for conversion", type="Cross")
			sys.exit(1)
		if apFile.fileSize(xthreedfile) < 1:
			self.writeToRunningLog("failed to open x3d file, file is empty", type="Cross")
			sys.exit(1)
		rootname = os.path.splitext(xthreedfile)[0]
		stlfile = rootname+".stl"

		assimpcli = os.environ.get("ASSIMP_CLI", "assimp")
		if shutil.which(assimpcli) is None:
			self.writeToRunningLog("assimp CLI was not found; please install assimp or set ASSIMP_CLI", type="Cross")
			sys.exit(1)

		convertcmd = "{} export {} {}".format(
			shlex.quote(assimpcli),
			shlex.quote(xthreedfile),
			shlex.quote(stlfile),
		)
		self.writeToRunningLog("Converting X3D to STL using assimp-cli (headless mesh export)")
		self.runCommand(convertcmd, verbose=True, source=False)

		if not os.path.isfile(stlfile):
			self.writeToRunningLog("FAILED to convert X3D into STL file: "+stlfile, type="Cross")
			sys.exit(1)
		self.writeToRunningLog("wrote STL file: "+stlfile, type="Check")
		self.writeToRunningLog("Mesh conversion completed in %s"%(apDisplay.timeString(time.time()-t0)))
		return stlfile

	#===========
	def getProgramPath(self, programname):
		programpath = os.path.join(apParam.getAppionDirectory(), 'bin', programname)
		if not os.path.isfile(programpath):
			result = subprocess.run(["which", programname], capture_output=True, text=True)
			path = result.stdout.strip()
			if path:
				programpath = path
		if not os.path.isfile(programpath):
			apDisplay.printWarning(programname+" was not found")
			for path in os.getenv("PATH", "").split(":"):
				apDisplay.printMsg("PATH: "+str(path))
			programpath = programname
		return programpath

	#====================
	def filterVolume(self, oldfilename, newfilename=None, radius=2.0):
		'''
		Filter volume for Chimera imaging using a Python low-pass filter.
		'''
		if newfilename is None:
			newfilename = oldfilename
		shrink = 2
		self.checkSystemLoad()
		self.writeToRunningLog("smoothing out volume (Python low-pass)")

		try:
			volume = mrc.read(oldfilename).astype(numpy.float32)
		except Exception:
			self.writeToRunningLog("failed to read volume for filtering", type="Cross")
			raise

		filtered = self._fermi_lowpass(volume, apix=1.0, cutoff=radius, rolloff=0.05)
		if shrink > 1:
			# Downsample to match prior shrink behavior
			zoom = 1.0 / shrink
			filtered = ndimage.zoom(filtered, zoom=zoom, order=1)

		filtered = self._normalize_volume(filtered)

		try:
			mrc.write(filtered, newfilename)
		except Exception:
			self.writeToRunningLog("failed to write filtered volume", type="Cross")
			raise

		if not os.path.isfile(newfilename):
			self.writeToRunningLog("failed to smooth volume", "cross")
			shutil.copy(oldfilename, newfilename)
			if not os.path.isfile(newfilename):
				self.writeToRunningLog("failed to copy volume", "cross")
				return oldfilename
		return newfilename

	#====================
	def makeImages(self, filename, sym='c1', contour=0.1, zoom=1.0, trim=False, pdbfile=None, print3d=False):
		t0 = time.time()

		### if using a pdbfile, cannot reset origin
		if pdbfile is not None or print3d is True:
			tempfile = filename
		else:
			### filter and center images
			tempfile = filename+".temp.mrc"
			tempfile = self.filterVolume(filename, tempfile)

		### create images
		link = re.sub("/var/www/html/3vee/output", self.output_url, filename)
		self.writeToRunningLog("imaging volume <a href='"+link+"'>(download mrc)</a> with headless renderer")
		try:
			mrc_size_mb = os.path.getsize(tempfile) / (1024.0 * 1024.0)
			vol_header = mrc.readHeaderFromFile(tempfile)
			dims = (vol_header.get('nx'), vol_header.get('ny'), vol_header.get('nz'))
			self.writeToRunningLog(f"volume shape {dims} size {mrc_size_mb:.2f} MB")
		except Exception as exc:
			self.writeToRunningLog(f"could not read volume metadata: {exc}", type="Star")

		try:
			apHeadlessRender.renderSnapshots(
				tempfile,
				contour=contour,
				zoom=zoom,
				sym=sym,
				silhouette=False,
				pdb=pdbfile,
				name=os.path.splitext(filename)[0],
				print3d=print3d,
			)
		except Exception as exc:
			self.writeToRunningLog(f"Renderer crashed: {exc}", type="Cross")
			return None, None
		if "temp" in tempfile:
			apFile.removeFile(tempfile)

		objfile = (os.path.splitext(filename)[0])+".obj"
		if os.path.isfile(objfile):
			self.writeToRunningLog("Renderer created Jmol compatible file")
			objfile = self.gzipFile(objfile)
		else:
			objfile = None

		x3dfile = (os.path.splitext(filename)[0])+".x3d"
		if os.path.isfile(x3dfile):
			self.writeToRunningLog("Renderer created 3D printing compatible file")
			objfile = x3dfile
			
		### look for files
		pngbase = os.path.splitext(filename)[0]
		pngfiles = glob.glob(pngbase+".*.png")
		if not len(pngfiles) > 0:
			self.writeToRunningLog(
				"Renderer failed to create images, no files. Dir contents: "
				+ ", ".join(sorted(os.listdir(os.path.dirname(filename)))),
				type="Cross",
			)
			return None, objfile
		else:
			png_info = []
			for pf in pngfiles:
				try:
					png_info.append(f"{os.path.basename(pf)} ({os.path.getsize(pf)/1024.0:.1f} KB)")
				except OSError:
					png_info.append(os.path.basename(pf))
			self.writeToRunningLog("png outputs: " + ", ".join(sorted(png_info)))

		### trim pngs
		if trim is True:
			self.checkSystemLoad()
			for pngfile in pngfiles:
				trimcmd = "mogrify -trim "+pngfile
				self.runCommand(trimcmd, verbose=False)

		self.writeToRunningLog("Rendering completed in %s"%(apDisplay.timeString(time.time()-t0)))

		return pngfiles, objfile

	#====================
	def animateGif(self, filename, sym='c1', contour=0.1, zoom=1.0):
		return None
		self.checkSystemLoad()
		self.writeToRunningLog("making animated gif")
		apHeadlessRender.renderAnimation(filename, contour=contour, zoom=zoom, sym=sym, silhouette=False)
		giffile = filename+".animate.gif"

		if not os.path.isfile(giffile):
			self.writeToRunningLog("ImageMagick failed to composite images", type="Cross")
			sys.exit(1)
		return giffile

	#====================
	def tarFiles(self, filelist):
		self.writeToRunningLog("tarring file list")
		self.checkSystemLoad()
		tarname = "archive.tar"
		if os.path.isfile(tarname):
			os.remove(tarname)
		tarcmd = "tar -cvf %s "%(tarname)
		for fname in filelist:
			basename = os.path.basename(fname)
			if os.path.isfile(basename):
				tarcmd += "%s "%(basename)
			elif os.path.isfile(basename+".gz"):
				tarcmd += "%s.gz "%(basename)
		self.runCommand(tarcmd, verbose=True)
		return tarname

	#====================
	def gzipFile(self, fname, pymol=False):
		self.writeToRunningLog("compressing "+os.path.basename(fname))
		self.checkSystemLoad()
		if pymol is True:
			header = mrc.readHeaderFromFile(fname)
			for key in list(header.keys()):
				xyz = ('x', 'y', 'z')
				if (key[0] in xyz or key[-1] in xyz) and not key.startswith('am'):
					#print key, header[key]
					continue
				else:
					del header[key]
			a = mrc.read(fname)
			b = numpy.array(a, dtype=numpy.float32)
			#print header
			mrc.write(b, fname, header=header)
			del a,b
		gzfname = fname+".gz"
		if os.path.isfile(gzfname):
			if os.path.isfile(fname):
				### files exists, overwrite it
				os.remove(gzfname)
			elif os.path.isfile(gzfname):
				### already compressed
				return gzfname
		gzcmd = "gzip -v9 "+fname
		self.runCommand(gzcmd, verbose=True)
		return gzfname

	#====================
	def writeToRunningLog(self, msg, type="Check"):
		print("Message: ", msg)
		logdir = os.path.dirname(self.runlogfile)
		try:
			if logdir and not os.path.isdir(logdir):
				os.makedirs(logdir, exist_ok=True)
			if os.path.isfile(self.runlogfile) or logdir:
				with open(self.runlogfile, "a") as f:
					f.write("<li class='"+type+"'>\n")
					f.write(str(msg)+"\n")
					f.write("<font size=-2><i>("+time.asctime()+")</i></font>\n")
					f.write("</li>\n")
		except Exception as exc:
			sys.stderr.write(f"Failed to write running log: {exc}\n")

	#====================
	def thousands(self, num):
		locale.setlocale(locale.LC_ALL, "")
		return locale.format_string('%d', num, grouping=True)

	#====================
	def docpop(self, key, text):
		key = key.lower()
		docstr = ("  <a href='#%s' id='l%s' onMouseOver='popLayer(\"%s\",\"l%s\")' onMouseOut='hideLayer()'>%s</a>"
			%(key, key, key, key, text))
		return docstr

	#====================
	def webMrcStats(self, mrcfile, apix, webf):
		t0 = time.time()
		self.writeToRunningLog("analyzing volume")
		webf.write("<table class='resultstable'>\n")
		webf.write("<tr><td align='center' colspan='3'>\n")
		webf.write("  <h3>Volume Information</h3>\n")
		voldata = mrc.read(mrcfile)

		webf.write("</td></tr><tr><td align='left'>\n")
		webf.write(self.docpop("gridres", "Voxel size:"))
		webf.write("</td><td align='right'>")
		webf.write("  %.1f &Aring;\n"%(apix))

		volume = voldata.sum()*apix**3
		webf.write("</td></tr><tr><td align='left'>\n")
		webf.write(self.docpop("volume", "Volume:"))
		webf.write("</td><td align='right'>")
		webf.write("  %s &Aring;<sup>3</sup>\n"%(self.thousands(volume)))

		binaryvol = numpy.where(voldata > 0.5, 1.0, 0.0)
		pixarea = surfarea.surfaceArea(binaryvol, test=False)
		area = pixarea*apix**2
		webf.write("</td></tr><tr><td align='left'>\n")
		webf.write(self.docpop("surfarea", "Surface area:"))
		webf.write("</td><td align='right'>")
		webf.write("  %s &Aring;<sup>2</sup>\n"%(self.thousands(area)))

		#webf.write("</td></tr><tr><td align='left'>\n")
		#webf.write("  Raw surface area")
		#webf.write("</td><td align='right'>")
		#webf.write("  %.1f &Aring;<sup>2</sup>\n"%(pixarea))

		sphericity = (36.0 * math.pi * volume**2)**(1/3.) / area 
		webf.write("</td></tr><tr><td align='left'>\n")
		webf.write(self.docpop("sphericity", "Sphericity, &Psi;:"))
		webf.write("</td><td align='right'>")
		webf.write("  %.2f \n"%(sphericity))

		webf.write("</td></tr><tr><td align='left'>\n")
		webf.write(self.docpop("effrad", "Effective radius:"))
		webf.write("</td><td align='right'>")
		webf.write("  %.2f &Aring;\n"%(3.0*volume/area))

		#webf.write("</td></tr><tr><td align='left'>\n")
		#webf.write("  Raw Center of mass")
		#webf.write("</td><td align='right'>")
		#webf.write("  (%.1f, %.1f, %.1f) &Aring;\n"%(com[0], com[1], com[2]))
		#webf.write("</td></tr><tr><td align='left'>\n")
		#webf.write("  Origin")
		#webf.write("</td><td align='right'>")
		#webf.write("  (%.1f, %.1f, %.1f) &Aring;\n"%(header['nxstart'], header['nystart'], header['nzstart']))

		centmass = self.centerOfMass(voldata, apix)
		webf.write("</td></tr><tr><td align='left'>\n")
		webf.write(self.docpop("com", "Center of Mass:"))
		webf.write("</td><td align='right'>")
		webf.write("  (%.1f, %.1f, %.1f) &Aring;\n"%(centmass))

		try:
			redcentmass = self.reducedCenterOfMass(voldata, apix)
			webf.write("</td></tr><tr><td align='left'>\n")
			webf.write(self.docpop("reducedcenter", "Reduced Center:"))
			webf.write("</td><td align='right'>")
			webf.write("  (%.1f, %.1f, %.1f) &Aring;\n"%(redcentmass))
		except:
			self.writeToRunningLog("reduced center failed")

		webf.write("</td></tr></table>\n")
		self.writeToRunningLog("volume analysis completed in %s"%(apDisplay.timeString(time.time()-t0)))

	#====================
	def centerOfMass(self, voldata, apix):
		labels,n = ndimage.label(voldata)
		if n == 0:
			self.writeToRunningLog("failed to label volume", "cross")
			com = ndimage.center_of_mass(voldata)
		else:
			com = ndimage.center_of_mass(voldata, labels, [1])[0]
		header = mrc.getHeader(voldata)
		xcom = (com[0]+header['nxstart'])*apix
		ycom = (com[1]+header['nystart'])*apix
		zcom = (com[2]+header['nzstart'])*apix
		self.writeToRunningLog("normal CoM (%.1f, %.1f, %.1f) &Aring;\n"%(xcom, ycom, zcom))
		return (xcom, ycom, zcom)

	#====================
	def reducedCenterOfMass(self, voldata, apix):
		tempdata = ndimage.minimum_filter(voldata, size=3)
		lastdata = None
		while tempdata.sum() > 0:
			lastdata = tempdata
			tempdata = ndimage.minimum_filter(tempdata, size=3)
		del tempdata
		if lastdata is None:
			return (0,0,0)
		labels,n = ndimage.label(lastdata)
		if n == 0:
			self.writeToRunningLog("failed to label volume", "cross")
			com = ndimage.center_of_mass(lastdata)
		else:
			com = ndimage.center_of_mass(lastdata, labels, [1])
		del lastdata
		header = mrc.getHeader(voldata)
		xcom = (com[0]+header['nxstart'])*apix
		ycom = (com[1]+header['nystart'])*apix
		zcom = (com[2]+header['nzstart'])*apix
		self.writeToRunningLog("reduced CoM (%.1f, %.1f, %.1f) &Aring;\n"%(xcom, ycom, zcom))
		return (xcom, ycom, zcom)

	#====================
	def webMrcSection(self, mrcfiles, website, webf, pdb=False, pymol=False):
		if isinstance(mrcfiles, str):
			mrcfiles = [mrcfiles]
		if not mrcfiles:
			return
		webf.write("<h3>Downloadable files of your surface:</h3>\n")
		webf.write("<table border='0'><tr><td align='left'>\n")
		webf.write("<h4><ul>\n")
		if len(mrcfiles) > 1:
			tarfile = self.tarFiles(mrcfiles)
		for mrcfile in mrcfiles:
			#webf.write("WATER PDB")
			if self.script.params['waterpdb'] is True:
				pdbfile = re.sub(".mrc", ".pdb", mrcfile)
				#webf.write("PDB file: "+pdbfile)
				gzpdbfile = self.gzipFile(pdbfile)
				#webf.write("Gzip PDB file: "+gzpdbfile)
				if os.path.isfile(gzpdbfile):
					webf.write("<li>download gzipped water PDB file: <a href='"
						+website+os.path.basename(gzpdbfile)+"'>"
						+os.path.basename(pdbfile)+"</a></li>\n")
			if mrcfile[-2:] != "gz":
				gzmrcfile = self.gzipFile(mrcfile, pymol)
			if os.path.isfile(gzmrcfile):
				webf.write("<li>download gzipped MRC file: <a href='"
					+website+os.path.basename(gzmrcfile)+"'>"
					+os.path.basename(mrcfile)+"</a></li>\n")
		if len(mrcfiles) > 1 and os.path.isfile(tarfile):
			webf.write("<li>download TAR archive of all gzipped MRC files: <a href='"
				+website+os.path.basename(tarfile)+"'>"
				+os.path.basename(tarfile)+"</a></li>\n")
		if pdb is True and self.pdbid is not None:
			webf.write("<li>download gzipped PDB of the original structure: <a href='"
				+self.pdburl+"'>"
				+self.pdbid+".pdb.gz</a></li>\n")
		webf.write("<li><font size='-1'>To view these files, use "
			+"<a href='http://www.cgl.ucsf.edu/chimera/'>UCSF Chimera</a> or "
			+"<a href='http://pymol.org/'>PyMol</a></font>")
		webf.write("<li><font size='-1'><a href='volumeviewing.php'>Volume Viewing Guide</a>"
			+" on how to view these files</font>")
		webf.write("</ul></h4>\n")
		webf.write("</td></tr></table>\n")

	#====================
	def webStlSection(self, stlfiles, website, webf, pdb=False):
		if isinstance(stlfiles, str):
			stlfiles = [stlfiles]
		if not stlfiles:
			return
		webf.write("<h3>Downloadable STL files of your structure for 3d printing:</h3>\n")
		webf.write("<table border='0'><tr><td align='left'>\n")
		webf.write("<h4><ul>\n")
		for stlfile in stlfiles:
			if os.path.isfile(stlfile):
				webf.write("<li>download STL file: <a href='"
					+website+os.path.basename(stlfile)+"'>"
					+os.path.basename(stlfile)+"</a></li>\n")
		if pdb is True and self.pdbid is not None:
			webf.write("<li>download gzipped PDB of the original structure: <a href='"
				+self.pdburl+"'>"
				+self.pdbid+".pdb.gz</a></li>\n")
		webf.write("<li><font size='-1'>To view open files, use "
			+"<a href='http://www.makerbot.com/blog/category/makerware/'>MakerBot MakerWare</a> or "
			+"<a href='http://meshlab.sourceforge.net/'>MeshLab</a></font>")
		webf.write("</ul></h4>\n")
		webf.write("</td></tr></table>\n")


	#====================
	def webImageSection(self, images, website, webf, title=None):
		if not images:
			return
		if title is None:
			title = "Images of your surface"
		webf.write("<br/><h3>"+title+":</h3>\n")
		images.sort()
		for imgfile in images:
			if os.path.isfile(imgfile):
				webimg = os.path.join(website, os.path.basename(imgfile))
				webf.write("<a href='"+webimg
					+"'>\n<img src='"+webimg+"' height='128'>\n</a>&nbsp;\n")
		webf.write("<br/>\n")

	#====================
	def webJmolSection(self, objfile, website, webf, pdbfile=None):
		print("OBJFILE", objfile)
		if not objfile or not os.path.isfile(objfile):
			return
		objlink = os.path.join(website, os.path.basename(objfile))
		weblink = "jmolViewer.php?objfile="+objlink
		if pdbfile is not None:
			pdblink = os.path.join(website, os.path.basename(pdbfile))
			weblink += "&pdbfile="+pdblink
		webf.write("<a href='"+weblink+"'>\nView Volume in Jmol\n</a>&nbsp;\n")
		webf.write("<br/>\n")

	#====================
	def __del__(self):
		self.writeToRunningLog("FINISHED")
		return

	#=====================
	def close(self):
		self.__del__()

#====================
#====================
#====================
if __name__ == "__main__":
	threev = ThreeVLib()
	pdbfile = threev.downloadPDB("1ehz")
	xyzrfile = threev.convertPDBtoXYZR(pdbfile, True)
	#fsv = threev.runFsvCalc(xyzrfile)
	#mrcfile = threev.runChannel(xyzrfile)
	mrcfile = threev.runVolume(xyzrfile, probe=4.0, gridsize=0.4)
	os.remove(xyzrfile)
	pngfiles = threev.makeImages(mrcfile)
	#os.remove(mrcfile)
	threev.gzipFile(mrcfile)
	print("SUCCESS")
