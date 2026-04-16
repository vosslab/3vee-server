#!/usr/bin/env python3

"""
Python program for running 3v FSV Calc
"""

import ThreeVScript

#=====================
#=====================
class RunThreeVScript(ThreeVScript.ThreeVScript):
	#=====================
	def setupParserOptions(self):
		self.parser.set_usage("Usage: %prog --rundir=<output dir> --jobid=<job id> --pdbid=<pdb id>")
		ThreeVScript.add_dual_probe_options(self.parser)

	#=====================
	def checkConflicts(self):
		return

	#====================
	#====================
	#====================
	def start(self):
		### run program
		mrcfile = self.threev.runTunnel(self.xyzrfile, bigprobe=self.params['bigprobe'],
			smallprobe=self.params['smallprobe'], gridsize=self.params['gridsize'])

		### make images
		pngfiles, objfile = self.threev.makeImages(mrcfile, pdbfile=self.pdbfile)
		### make animated gif
		#giffile = self.threev.animateGif(pngfiles)

		### write to webpage
		self.write_single_mrc_results_page(mrcfile, pngfiles, objfile)



#====================
#====================
#====================
if __name__ == "__main__":
	runthreev = RunThreeVScript()
	runthreev.start()
	runthreev.close()







