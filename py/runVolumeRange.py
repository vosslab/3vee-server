#!/usr/bin/env python3

"""
Python program for running 3v Volume
"""

import os
import numpy
import ThreeVScript

#=====================
#=====================
class RunThreeVScript(ThreeVScript.ThreeVScript):
	#=====================
	def setupParserOptions(self):
		self.parser.set_usage("Usage: %prog --rundir=<output dir> --jobid=<job id> --pdbid=<pdb id>")
		self.parser.add_option("--minprobe", dest="minprobe", type="float", default=0.0,
			help="Probe radius", metavar="#")
		self.parser.add_option("--maxprobe", dest="maxprobe", type="float", default=10.0,
			help="Probe radius", metavar="#")
		self.parser.add_option("--probestep", dest="probestep", type="float", default=1.0,
			help="Probe radius", metavar="#")

	#=====================
	def checkConflicts(self):
		return

	#====================
	#====================
	#====================
	def start(self):
		a = self.params['minprobe']
		b = self.params['maxprobe']+self.params['probestep']
		c = self.params['probestep']

		f = open("results-"+self.params['jobid']+".html", "w")
		mrclist = []
		for probe in numpy.arange(a,b,c):
			self.threev.writeToRunningLog("starting probe size %.3f"%(probe))

			#### set mrc name
			root = os.path.splitext(self.xyzrfile)[0]
			mrcfile = ("%s-%03.1f.mrc"%(root, probe))

			#### run program
			mrcfile = self.threev.runVolume(self.xyzrfile,
				probe=probe, gridsize=self.params['gridsize'],
				mrcfile=mrcfile)

			### make images
			pngfiles, objfile = self.threev.makeImages(mrcfile)

			mrclist.append(mrcfile)

			### write to webpage
			title = "Images of your surface at probe size: %.3f"%(probe)
			self.threev.webImageSection(pngfiles, self.website, f, title=title)
			self.threev.webJmolSection(objfile, self.website, f)
			self.threev.webMrcStats(mrcfile, self.params['gridsize'], f)
			self.threev.webMrcSection([mrcfile], self.website, f, pdb=True, pymol=self.params['pymol'])
			f.write("<hr/><hr/>\n")

		self.threev.webMrcSection(mrclist, self.website, f)
		f.close()



#====================
#====================
#====================
if __name__ == "__main__":
	runthreev = RunThreeVScript()
	runthreev.start()
	runthreev.close()






