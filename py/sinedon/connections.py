from sinedon import dbconfig
from sinedon.dbdatakeeper import DBDataKeeper as DB
import atexit
import threading

lock = threading.Lock()
connections = {}

def _close_all_connections():
	for entry in connections.values():
		try:
			entry['connection'].close()
		except:
			pass
	connections.clear()

atexit.register(_close_all_connections)

def tail(modulename):
	return modulename.split('.')[-1]

def getConnection(modulename):
	lock.acquire()
	try:
		if not isinstance(modulename, str):
			modulename = modulename.__name__
		modulename = tail(modulename)
		if modulename not in connections:
			connectedconf = None
		else:
			connectedconf = connections[modulename]['config']
		dbconf = dbconfig.getConfig(modulename)

		if dbconf != connectedconf:
			#print 'MAKING CONNECTION', modulename, dbconf
			connections[modulename] = {'config': dbconf, 'connection': DB(**dbconf)}
		connection = connections[modulename]['connection']
	finally:
		lock.release()
	return connection
