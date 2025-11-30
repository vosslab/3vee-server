#!/usr/bin/env python3

"""
Python program for running 3v Volume
"""

import ThreeVScript

#=====================
#=====================
class RunThreeVScript(ThreeVScript.ThreeVScript):
	#=====================
	def setupParserOptions(self):
		self.parser.set_usage("Usage: %prog --rundir=<output dir> --jobid=<job id> --pdbid=<pdb id>")
		self.parser.add_option("--probe", dest="probe", type="float", default=3.0,
			help="Probe radius", metavar="#")

	#=====================
	def checkConflicts(self):
		return

	#====================
	#====================
	#====================
	def start(self):
		#### run program
		mrcfile = self.threev.runVolume(self.xyzrfile, 
			probe=self.params['probe'], gridsize=self.params['gridsize'])

		### make images
		pngfiles, objfile = self.threev.makeImages(mrcfile)

		### write to webpage
		f = open("results-"+self.params['jobid']+".html", "w")
		self.threev.webImageSection(pngfiles, self.website, f)
		self.threev.webJmolSection(objfile, self.website, f)
		self.threev.webMrcStats(mrcfile, self.params['gridsize'], f)
		self.threev.webMrcSection([mrcfile], self.website, f, pdb=True, pymol=self.params['pymol'])
		f.close()
		


#====================
#====================
#====================
if __name__ == "__main__":
	runthreev = RunThreeVScript()
	runthreev.start()
	runthreev.close()	







