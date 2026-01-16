"""
Backward-compat shim: apChimera is now apHeadlessRender.
Importing this module will pull the new implementation.
"""

from appionlib import apHeadlessRender as _apHeadlessRender

__all__ = [name for name in dir(_apHeadlessRender) if not name.startswith("_")]

def __getattr__(name):
	return getattr(_apHeadlessRender, name)

def __dir__():
	return sorted(set(globals().keys()) | set(dir(_apHeadlessRender)))
