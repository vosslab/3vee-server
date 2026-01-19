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
		self.parser.add_option("--bigprobe", dest="bigprobe", type="float", default=6.0,
			help="Probe radius", metavar="#")
		self.parser.add_option("--smallprobe", dest="smallprobe", type="float", default=2.0,
			help="Probe radius", metavar="#")

	#=====================
	def checkConflicts(self):
		return

	#====================
	#====================
	#====================
	def start(self):
		### run program
		mrcfile = self.threev.runSolvent(self.xyzrfile, bigprobe=self.params['bigprobe'],
			smallprobe=self.params['smallprobe'], gridsize=self.params['gridsize'])

		### make images
		pngfiles, objfile = self.threev.makeImages(mrcfile, pdbfile=self.pdbfile)
		### make animated gif
		#giffile = self.threev.animateGif(pngfiles)

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







