#!/usr/bin/python -O

"""
Python program for running 3v FSV Calc
"""

import ThreeVScript

#=====================
#=====================
class RunFSVCalcScript(ThreeVScript.ThreeVScript):
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
		#get pdb
		if not self.params['pdbfile']:
			pdbfile = self.threev.downloadPDB(self.params['pdbid'])
		else:
			pdbfile = os.path.basename(self.params['pdbfile'])
			shutil.copy(self.params['pdbfile'], self.params['rundir'])
		#convert pdb
		xyzrfile = self.threev.convertPDBtoXYZR(pdbfile, self.params['hetero'])
		#run program
		fsvdata = self.threev.runFsvCalc(xyzrfile, bigprobe=self.params['bigprobe'],
			 smallprobe=self.params['smallprobe'], gridsize=self.params['gridsize'])
		ezdfile = fsvdata['ezdfile']
		os.remove(xyzrfile)
		#convert ezd
		ccp4file = self.threev.convertEZDtoCCP4(ezdfile)
		#convert ccp4 to mrc
		mrcfile = self.threev.convertCCP4toMRC(ccp4file)
		#make images
		pngfiles, objfile = self.threev.makeImages(mrcfile)
		#make animated gif
		giffile = self.threev.animateGif(pngfiles)
		#zip file
		self.threev.gzipFile(ccp4file)
		self.threev.gzipFile(mrcfile)
		#os.remove(ccp4file)
		self.threev.close()

		f = open("results-"+self.params['jobid']+".html", "w")
		website = "output/results/"+self.params['jobid']+"/"

		### Statistics of your 
		f.write("<br/><h3>Statistics of your internal solvent:</h3>\n")
		f.write("<table><tr><td><h4><ul>\n")
		for key in fsvdata.keys():
			if key != 'ezdfile':
				f.write("<li>"+str(key)+":&nbsp;\t"+str(fsvdata[key])+"</li>\n")
		f.write("</ul></h4></td></tr></table>\n")

		### Downloadable files of the volume
		f.write("<br/><h3>Downloadable files of your internal solvent:</h3>\n")
		f.write("<h4><ul>\n")
		if os.path.isfile(ezdfile+".gz"):
			f.write("<li>download EZD file: <a href='"
				+website+os.path.basename(ezdfile)+".gz'>"
				+os.path.basename(ezdfile)+"</a></li>\n")
		if os.path.isfile(ccp4file+".gz"):
			f.write("<li>download CCP4 file: <a href='"
				+website+os.path.basename(ccp4file)+".gz'>"
				+os.path.basename(ccp4file)+"</a></li>\n")
		if os.path.isfile(mrcfile+".gz"):
			f.write("<li>download MRC file: <a href='"
				+website+os.path.basename(mrcfile)+".gz'>"
				+os.path.basename(mrcfile)+"</a></li>\n")
		f.write("</ul>To view these files, use "
			+"<a href='http://www.cgl.ucsf.edu/chimera/'>UCSF Chimera</a> or "
			+"<a href='http://pymol.org/'>PyMol</a>")
		f.write("</h4>\n")

		### Images of the volume
		pngfiles.sort()
		if pngfiles or os.path.isfile(giffile):
			f.write("<br/><h3>Images of your internal solvent:</h3>\n")
		if os.path.isfile(giffile):
			f.write("<a href='"+website+os.path.basename(giffile)
				+"'>\n<img src='output/results/"+self.params['jobid']+"/"
				+os.path.basename(giffile)+"' width='256' height='256'>\n</a>&nbsp;\n")		
		elif pngfiles:
			for pngfile in pngfiles:
				if os.path.isfile(pngfile):
					f.write("<a href='"+website+os.path.basename(pngfile)
						+"'>\n<img src='output/results/"+self.params['jobid']+"/"
						+os.path.basename(pngfile)+"' width='128' height='128'>\n</a>&nbsp;\n")
		f.close()	
		


#====================
#====================
#====================
if __name__ == "__main__":
	runFSVCalc = RunFSVCalcScript()
	runFSVCalc.start()
	runFSVCalc.close()	







