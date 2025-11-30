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
		self.parser.add_option("--coord", dest="coord", default="0,0,0",
			help="X,Y,Z coordinate of channel", metavar="#,#,#")

	#=====================
	def checkConflicts(self):
		if not "," in self.params['coord']:
			self.threev.writeToRunningLog("could not parse coordinate: "+self.params['coord'], "Cross")
			raise
		clist = self.params['coord'].split(",")
		self.coord_list = []
		for xyz in clist:
			self.coord_list.append(float(xyz))
		if len(self.coord_list) < 3:
			self.threev.writeToRunningLog("could not parse coordinate: "+self.params['coord'], "Cross")
			raise
		return

	#====================
	#====================
	#====================
	def start(self):
		### run program
		mrcfile = self.threev.runChannel(self.xyzrfile, bigprobe=self.params['bigprobe'],
			smallprobe=self.params['smallprobe'], gridsize=self.params['gridsize'], 
			xyzcoord=self.coord_list)

		### make images
		pngfiles, objfile = self.threev.makeImages(mrcfile)

		### write to webpage
		f = open("results-"+self.params['jobid']+".html", "w")

		self.threev.webImageSection(pngfiles, self.website, f)
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







