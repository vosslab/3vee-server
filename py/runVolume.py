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
		self.write_single_mrc_results_page(mrcfile, pngfiles, objfile)



#====================
#====================
#====================
if __name__ == "__main__":
	runthreev = RunThreeVScript()
	runthreev.start()
	runthreev.close()







