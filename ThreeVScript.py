#!/usr/bin/python -O

#builtin
import sys
import os
import re
import time
import math
import shutil
import random
import cPickle
from appionlib import apDisplay
from appionlib import apParam
from string import lowercase
from optparse import OptionParser
import ThreeVLib
import threevdata

class ThreeVScript(object):
	#=====================
	def __init__(self):
		self.t0 = time.time()
		self.argdict = {}
		self.optdict = {}
		self.timestamp = apParam.makeTimestamp()
		self.functionname = apParam.getFunctionName(sys.argv[0])
		apParam.setUmask()

		### setup default parser: output directory, etc.
		self.parser = OptionParser()
		self.setupGlobalParserOptions()
		self.setupParserOptions()
		self.params = self.convertParserToParams(self.parser)
		self.datestamp = self.params['jobid'][:7]
		self.jobdir = re.sub('\.', '/', self.params['jobid'])

		#init threev
		self.threev = ThreeVLib.ThreeVLib(jobid=self.params['jobid'])
		self.threev.script = self
		self.threev.writeToRunningLog("host ip address="+str(self.params['hostip']))

		### check if user wants to print help message
		self.checkGlobalConflicts()
		self.checkConflicts()

		### setup output directory
		self.setupOutputDirectory()

		### write function log
		self.runlogfile = "running-"+self.params['jobid']+".html"
		self.functionlogfile = apParam.writeFunctionLog(sys.argv, msg=False)

		### upload command line parameters to database
		self.uploadScriptData()

		### any custom init functions go here
		self.onInit()
		self.website = os.path.join("output/", self.jobdir)+"/"

		### get pdb
		if not self.params['pdbfile']:
			self.pdbfile = self.threev.downloadPDB(self.params['pdbid'], biounit=self.params['biounit'])
		else:
			shutil.copy(self.params['pdbfile'], self.params['rundir'])
			self.pdbfile = os.path.join(self.params['rundir'], os.path.basename(self.params['pdbfile']))
		### convert pdb
		self.xyzrfile = self.threev.convertPDBtoXYZR(self.pdbfile, self.params['hetero'])

	#=====================
	def argumentFromParamDest(self, dest):
		"""
		For a given optparse destination (dest, e.g., 'runname') 
			this will determine the command line
			argument (e.g., -n)
		"""
		if len(self.argdict) == 0:
			for opt in self.parser.option_list:
				arg = str(opt.get_opt_string.im_self)
				if '/' in arg:
					args = arg.split('/')
					arg = args[-1:][0]
				self.argdict[opt.dest] = arg
				self.optdict[opt.dest] = opt
		if dest in self.argdict:
			return self.argdict[dest]
		return "????"

	#=====================
	def usageFromParamDest(self, dest, value):
		"""
		For a given optparse destination (dest, e.g., 'commit') 
			and value (e.g., 'False') this will generate the command line
			usage (e.g., '--no-commit')
		"""
		usage = None
		if value is None:
			return None
		argument = self.argumentFromParamDest(dest)
		if not dest in self.optdict:
			return None
		optaction = self.optdict[dest].action
		if optaction == 'store':
			opttype = self.optdict[dest].type
			value = str(value)
			if not ' ' in value:
				usage = argument+"="+value
			else:
				usage = argument+"='"+value+"'"
		elif optaction == 'store_true' or optaction == 'store_false':
			storage = 'store_'+str(value).lower()
			for opt in self.parser.option_list:
				if opt.dest == dest and opt.action == storage:
					arg = str(opt.get_opt_string.im_self)
					if '/' in arg:
						args = arg.split('/')
						arg = args[-1:][0]
					usage = arg
		return usage

	#=====================
	def uploadScriptData(self):
		"""
		Using tables to track program run parameters in a generic fashion
		inspired by Roberto Marabini and Carlos Oscar Sanchez Sorzano from the Xmipp team/Carazo lab
		"""
		pathq = threevdata.Path()
		pathq['path'] = self.params['rundir']

		prognameq = threevdata.ProgramName()
		prognameq['name'] = self.functionname

		userq = threevdata.UserName()
		userq['name'] = apParam.getUsername()

		hostq = threevdata.HostName()
		hostq['name'] = apParam.getHostname()

		localhostq = threevdata.HostName()
		localhostq['name'] = apParam.getHostname()
		localhostq['ip'] = apParam.getHostIP()
		localhostq['system'] = apParam.getSystemName()
		localhostq['distro'] = apParam.getLinuxDistro()
		localhostq['arch'] = apParam.getMachineArch()

		remotehostq = threevdata.HostName()
		remotehostq['ip'] = self.params['hostip']
		try:
			remotehostname = socket.gethostbyaddr(self.params['hostip'])[0]
			remotehostq['name'] = remotehostname
		except:
			pass

		progrunq = threevdata.ProgramRun()
		progrunq['progname'] = prognameq
		progrunq['username'] = userq
		progrunq['jobid'] = self.params['jobid']
		progrunq['localhost'] = localhostq
		progrunq['remotehost'] = remotehostq
		progrunq['allowuse'] = self.params['allowuse']
		progrunq['exemplar'] = False
		progrunq['path'] = pathq
		progrunq.insert()

		for paramname in self.params.keys():
			paramnameq = threevdata.ParamName()
			paramnameq['name'] = paramname
			paramnameq['progname'] = prognameq

			paramvalueq = threevdata.ParamValue()
			paramvalueq['value'] = str(self.params[paramname])
			usage = self.usageFromParamDest(paramname, self.params[paramname])
			paramvalueq['usage'] = usage
			paramvalueq['paramname'] = paramnameq
			paramvalueq['progrun'] = progrunq
			paramvalueq.insert()

	#=====================
	def checkGlobalConflicts(self):
		self.params['gridsize'] = self.convertGridResToGridSize(self.params['gridres'])
		if self.params['jobid'] is None:
			threev.writeToRunningLog("Please specify a jobid, e.g. --jobid=08jun04b", "Cross")
		if self.params['pdbfile'] is not None and self.params['pdbid'] is not None:
			threev.writeToRunningLog("Both pdbid and pdbfile were specified", "Cross")

	#=====================
	def setupGlobalParserOptions(self):
		self.parser.set_usage("Usage: %prog --rundir=<output dir> --jobid=<job id> --pdbid=<pdb id>")
		self.parser.add_option("--rundir", dest="rundir",
			help="Location to store output files", metavar="PATH")
		self.parser.add_option("-j", "--jobid", dest="jobid",
			help="Unique Job ID for the run", metavar="ID")
		self.parser.add_option("-p", "--pdbid", dest="pdbid",
			help="PDB ID for the run", metavar="ID")
		self.parser.add_option("-f", "--pdbfile", dest="pdbfile",
			help="PDB file for the run", metavar="FILE")
		self.parser.add_option("--hostip", dest="hostip",
			help="IP address of the hostname", metavar="ID")
		self.parser.add_option("--gridres", dest="gridres",
			help="Grid resolution for 3v programs", metavar="ID")
		self.parser.add_option("--hetero", dest="hetero", default=False,
			action="store_true", help="Use hetero atoms")
		self.parser.add_option("--biounit", dest="biounit", default=False,
			action="store_true", help="Use biological unit instead")
		self.parser.add_option("--allowuse", dest="allowuse", default=False,
			action="store_true", help="Allow publication of results")
		self.parser.add_option("--pymol", dest="pymol", default=False,
			action="store_true", help="Make volume compatible with PyMOL")
		self.parser.add_option("--waterpdb", dest="waterpdb", default=False,
			action="store_true", help="Create PDB file with water atoms at each voxel")

	#=====================
	def convertGridResToGridSize(self, gridres):
		if gridres == "crude":
			return 2.0
		elif gridres == "low":
			return 1.0
		elif gridres == "medium":
			return 0.75
		elif gridres == "high":
			return 0.5
		else:
			return 1.0

	#=====================
	def setRunDir(self):
		self.params['rundir'] = os.path.join(self.threev.procdir, "output/", self.jobdir)
		return

	#=====================
	def setupOutputDirectory(self):
		#IF NO rundir IS SET
		if self.params['rundir'] is None:
			self.setRunDir()
		#create the output directory, if needed
		apDisplay.printMsg("Output directory: "+self.params['rundir'])
		apParam.createDirectory(self.params['rundir'])
		os.chdir(self.params['rundir'])

	#=====================
	def convertParserToParams(self, parser):
		parser.disable_interspersed_args()
		(options, args) = parser.parse_args()
		if len(args) > 0:
			apDisplay.printError("Unknown commandline options: "+str(args))
		if len(sys.argv) < 2:
			parser.print_help()
			parser.error("no options defined")

		params = {}
		for i in parser.option_list:
			if isinstance(i.dest, str):
				params[i.dest] = getattr(options, i.dest)
		return params

	#=====================
	def writeFunctionLog(self, cmdlist, params=None, logfile=None, msg=True):
		"""
		Used by appionLoop
		"""
		if logfile is not None:
			pass
		elif params is not None and 'functionLog' in params and params['functionLog'] is not None:
			logfile = self.params['functionLog']
		else:
			logfile = apParam.getFunctionName(sys.argv[0])+".log"
		if msg is True:
			apDisplay.printMsg("writing function log to: "+logfile)
		#WRITE INFO
		try:
			user = os.getlogin() #os.environ.get('USER')
		except:
			user = "user.unknown"
		try:
			host = socket.gethostname()
		except:
			host = "host.unknown"
		timestamp = "[ "+user+"@"+host+": "+time.asctime()+" ]\n"
		out=""
		f=open(logfile,'a')
		f.write(timestamp)
		f.write(os.path.abspath(cmdlist[0])+" \\\n  ")
		for arg in cmdlist[1:]:
			if len(out) > 60 or len(out)+len(arg) > 90:
				f.write(out+"\\\n")
				out = "  "
			#if ' ' in arg and ('=' in arg or not '-' in arg):
			if ' ' in arg and '=' in arg:
				elems = arg.split('=')
				out += elems[0]+"='"+elems[1]+"' "
			else:
				out += arg+" "
		f.write(out+"\n")
		f.close()
		return logfile

	#=====================
	def __del__(self):
		self.onClose()
		self.threev.__del__()
		apParam.closeFunctionLog(functionname=self.functionname, logfile=self.functionlogfile, msg=False)
		apDisplay.printMsg("rundir:\n "+self.params['rundir'])
		apDisplay.printColor("COMPLETE SCRIPT:\t"+apDisplay.timeString(time.time()-self.t0),"green")

	#=====================
	def close(self):
		self.__del__()

	#=====================
	#=====================
	#=====================
	def onInit(self):
		return
	#=====================
	def setupParserOptions(self):
		self.parser.set_usage("Usage: %prog --rundir=<output dir> --jobid=<job id> --pdbid=<pdb id>")
	#=====================
	def checkConflicts(self):
		return
	#=====================
	def onClose(self):
		return



