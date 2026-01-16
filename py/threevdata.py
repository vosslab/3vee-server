import sinedon.data
Data = sinedon.data.Data

# Expose module under its own name so sinedon.maketables can import it by string
import sys
threevdata = sys.modules[__name__]

class Path(Data):
	def typemap(cls):
		return Data.typemap() + (
			('path', str),
		)
	typemap = classmethod(typemap)

class ProgramRun(Data):
	def typemap(cls):
		return Data.typemap() + (
			('jobid', str),
			('allowuse', bool),
			('exemplar', bool),
			('progname', ProgramName),
			('path', Path),
			('username', UserName),
			('localhost', HostName),
			('remotehost', HostName),
		)
	typemap = classmethod(typemap)

class ProgramName(Data):
	def typemap(cls):
		return Data.typemap() + (
			('name', str),
		)
	typemap = classmethod(typemap)

class ParamName(Data):
	def typemap(cls):
		return Data.typemap() + (
			('name', str),
			('progname', ProgramName),
		)
	typemap = classmethod(typemap)

class ParamValue(Data):
	def typemap(cls):
		return Data.typemap() + (
			('value', str),
			('usage', str),
			('paramname', ParamName),
			('progrun', ProgramRun),
		)
	typemap = classmethod(typemap)

class UserName(Data):
	def typemap(cls):
		return Data.typemap() + (
			('name', str),
		)
	typemap = classmethod(typemap)

class HostName(Data):
	def typemap(cls):
		return Data.typemap() + (
			('name', str),
			('ip', str),
			('system', str),
			('distro', str),
			('arch', str),
		)
	typemap = classmethod(typemap)
