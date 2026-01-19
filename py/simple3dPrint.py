
"""
Python program for running 3v Volume
"""

import os
import ThreeVScript
from appionlib import apFile

#=====================
#=====================
class RunThreeVScript(ThreeVScript.ThreeVScript):
	#=====================
	def setupParserOptions(self):
		self.parser.set_usage("Usage: %prog --rundir=<output dir> --jobid=<job id> --pdbid=<pdb id>")
		self.parser.add_option("--probe", dest="probe", type="float", default=3.0,
			help="Probe radius", metavar="#")
		self.parser.add_option("--flatmethod", dest="flatmethod", type="str", default="trim",
			help="Method to obtain flat surface", metavar="#")
		self.parser.add_option("--flataxis", dest="flataxis", type="str",
			help="Axis on which to obtain flat surface", metavar="#")
		self.parser.add_option("--trimpercent", dest="trimpercent", type="float",
			help="Percent to trim volume", metavar="#")

	#=====================
	def checkConflicts(self):
		return

	#====================
	#====================
	#====================
	def start(self):
		#### run program
		mrcfile = self.threev.runVolumeNoCav(self.xyzrfile,
			probe=self.params['probe'], gridsize=self.params['gridsize'])


		if self.params['flatmethod'] == 'trim':
			trimMrcFile = self.threev.trimMrcFile(mrcfile, self.params['flataxis'], self.params['trimpercent'])
			if trimMrcFile is None or not os.path.isfile(trimMrcFile):
				return
			apFile.removeFile(mrcfile)
			mrcfiles = [trimMrcFile]
		elif self.params['flatmethod'] == 'bisect':
			bisectMrcFile1, bisectMrcFile2 = self.threev.bisectMrcFile(mrcfile, self.params['flataxis'])
			if bisectMrcFile1 is None or not os.path.isfile(bisectMrcFile2):
				return
			apFile.removeFile(mrcfile)
			mrcfiles = [bisectMrcFile1, bisectMrcFile2]
		else:
			mrcfiles = [mrcfile]

		### write to webpage
		f = open("results-"+self.params['jobid']+".html", "w")
		for mrcfile in mrcfiles:
			pngfiles0, xthreedfile = self.threev.makeImages(mrcfile, print3d=True)
			self.threev.webImageSection(pngfiles0, self.website, f)
			self.threev.webMrcStats(mrcfile, self.params['gridsize'], f)
			apFile.removeFile(mrcfile)
			stlfile = self.threev.meshlabDecimateConvert(xthreedfile)
			if stlfile is None or not os.path.isfile(stlfile):
				return
			apFile.removeFile(xthreedfile)
			self.threev.webStlSection([stlfile], self.website, f)
		f.close()

#====================
#====================
#====================
if __name__ == "__main__":
	runthreev = RunThreeVScript()
	runthreev.start()
	runthreev.close()







