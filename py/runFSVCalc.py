#!/usr/bin/env python3

"""
Python program for running 3v FSV Calc
"""

import os
import shutil
import ThreeVScript

#=====================
#=====================
class RunFSVCalcScript(ThreeVScript.ThreeVScript):
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
		ezdfile = fsvdata.get('ezdfile')
		mrcfile = fsvdata.get('mrcfile')
		os.remove(xyzrfile)
		if mrcfile is None:
			self.threev.writeToRunningLog("FSVCalc did not produce an MRC file", type="Cross")
			self.threev.close()
			return
		#make images
		pngfiles, objfile = self.threev.makeImages(mrcfile)
		#make animated gif
		giffile = self.threev.animateGif(pngfiles)
		#zip file
		if ezdfile and os.path.isfile(ezdfile):
			self.threev.gzipFile(ezdfile)
		self.threev.gzipFile(mrcfile)
		# gzip CCP4 file if it exists
		basename = os.path.splitext(mrcfile)[0]
		ccp4file = basename + ".ccp4"
		if os.path.isfile(ccp4file):
			self.threev.gzipFile(ccp4file)
		self.threev.close()

		f = open("results-"+self.params['jobid']+".html", "w")
		website = "output/results/"+self.params['jobid']+"/"

		### Statistics of your
		f.write("<br/><h3>Statistics of your internal solvent:</h3>\n")
		f.write("<table><tr><td><h4><ul>\n")
		for key in list(fsvdata.keys()):
			if key != 'ezdfile':
				f.write("<li>"+str(key)+":&nbsp;\t"+str(fsvdata[key])+"</li>\n")
		f.write("</ul></h4></td></tr></table>\n")

		### Downloadable files of the volume
		f.write("<br/><h3>Downloadable files of your internal solvent:</h3>\n")
		f.write("<h4><ul>\n")
		if ezdfile and os.path.isfile(ezdfile+".gz"):
			f.write("<li>download EZD file: <a href='"
				+website+os.path.basename(ezdfile)+".gz'>"
				+os.path.basename(ezdfile)+"</a></li>\n")
		if os.path.isfile(mrcfile+".gz"):
			f.write("<li>download MRC file: <a href='"
				+website+os.path.basename(mrcfile)+".gz'>"
				+os.path.basename(mrcfile)+"</a></li>\n")
		if os.path.isfile(ccp4file+".gz"):
			f.write(f"<li>download CCP4 file "
				f"(for PyMOL and other CCP4 map readers): <a href='"
				f"{website}{os.path.basename(ccp4file)}.gz'>"
				f"{os.path.basename(ccp4file)}</a></li>\n")
		f.write("</ul>Use MRC files with "
			+"<a href='https://www.cgl.ucsf.edu/chimerax/'>ChimeraX</a>/"
			+"<a href='http://www.cgl.ucsf.edu/chimera/'>Chimera</a>. "
			+"Use CCP4 files with "
			+"<a href='http://pymol.org/'>PyMOL</a>.")
		f.write("</h4>\n")

		### Images of the volume
		pngfiles.sort()
		if pngfiles or (giffile and os.path.isfile(giffile)):
			f.write("<br/><h3>Images of your internal solvent:</h3>\n")
		if giffile and os.path.isfile(giffile):
			f.write("<a href='"+website+os.path.basename(giffile)
				+"'>\n<img src='output/results/"+self.params['jobid']+"/"
				+os.path.basename(giffile)+"' width='256' height='256'>\n</a>&nbsp;\n")
		elif pngfiles:
			for pngfile in pngfiles:
				if os.path.isfile(pngfile):
					f.write("<a href='"+website+os.path.basename(pngfile)
						+"'>\n<img src='output/results/"+self.params['jobid']+"/"
						+os.path.basename(pngfile)+"' width='128' height='128'>\n</a>&nbsp;\n")
		self.threev.webJmolSection(objfile, website, f, pdbfile=self.pdbfile)
		f.close()



#====================
#====================
#====================
if __name__ == "__main__":
	runFSVCalc = RunFSVCalcScript()
	runFSVCalc.start()
	runFSVCalc.close()

