#!/usr/bin/python -O

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
		self.parser.add_option("--minpercent", dest="minpercent", type="float",
			help="Minimum size of a channel", metavar="#")
		self.parser.add_option("--minvolume", dest="minvolume", type="int",
			help="Minimum volume of a channel", metavar="#")
		self.parser.add_option("--numchan", dest="numchan", type="int",
			help="Get N number of largest channels", metavar="#")

	#=====================
	def checkConflicts(self):
		if not self.params['numchan'] and not self.params['minvolume'] and not self.params['minpercent']:
			self.threev.writeToRunningLog("Please enter one of min volume, min percent or number of channels", "Cross")
			raise
		return

	#====================
	#====================
	#====================
	def start(self):
		### run program
		mrcfiles = self.threev.runChannelFinder(self.xyzrfile, bigprobe=self.params['bigprobe'],
			smallprobe=self.params['smallprobe'], gridsize=self.params['gridsize'], 
			minvolume=self.params['minvolume'], minpercent=self.params['minpercent'],
			numchan=self.params['numchan'])

		f = open("results-"+self.params['jobid']+".html", "w")
		count=0
		for mrcfile in mrcfiles:
			count+=1
			### make images
			pngfiles, objfile = self.threev.makeImages(mrcfile, pdbfile=self.pdbfile)
			### write to webpage
			title = "Images of channel %d"%(count)
			self.threev.webImageSection(pngfiles, self.website, f, title=title)
			self.threev.webJmolSection(objfile, self.website, f, pdbfile=self.pdbfile)
			self.threev.webMrcStats(mrcfile, self.params['gridsize'], f)
			self.threev.webMrcSection([mrcfile], self.website, f, pymol=self.params['pymol'])
			f.write("<hr/><hr/>\n")

		self.threev.webMrcSection(mrcfiles, self.website, f, pdb=True, pymol=self.params['pymol'])
		f.close()
		


#====================
#====================
#====================
if __name__ == "__main__":
	runthreev = RunThreeVScript()
	runthreev.start()
	runthreev.close()	







