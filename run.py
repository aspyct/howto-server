import sys
import os.path
from glob import glob

SRC_DIR="src"
VENDOR_DIR="vendor"

# find the location of this script 
mydir = os.path.dirname(os.path.realpath(__file__))

# add the src folder to the path
src_dir = os.path.join(mydir, SRC_DIR)
sys.path.insert(0, src_dir)

# add dependencies to the path as well
# all dependencies are in vendor/<vendor>/<libname>
lib_pattern = os.path.join(mydir, VENDOR_DIR, "*", "*")
for library_path in glob(lib_pattern):
    sys.path.insert(1, library_path)

# note that we insert'ed into sys.path rather than appending
# that way we're sure that our modules are loaded first

# all set! Load the app and let go

import cherrypy
import howto

server = howto.Server()
cherrypy.quickstart(server)

