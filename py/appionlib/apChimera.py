"""
Backward-compat shim: apChimera is now apHeadlessRender.
Importing this module will pull the new implementation.
"""

from appionlib.apHeadlessRender import *  # noqa: F401,F403
