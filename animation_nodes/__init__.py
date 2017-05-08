'''
Copyright (C) 2017 Jacques Lucke
mail@jlucke.com

Created by Jacques Lucke

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


bl_info = {
    "name":        "Animation Nodes",
    "description": "Node based visual scripting system designed for motion graphics in Blender.",
    "author":      "Jacques Lucke",
    "version":     (1, 7, 5),
    "blender":     (2, 78, 0),
    "location":    "Node Editor",
    "category":    "Node",
    "warning":     "This is no official release, it's still work in progress"
    }



# Test Environment
##################################

import traceback
from os import listdir
from os.path import dirname
addonsDirectory = dirname(dirname(__file__))
counter = 0
for name in listdir(addonsDirectory):
    name = name.lower()
    if "animation" in name and "nodes" in name and not "test" in name:
        counter += 1

if counter > 1:
    message = ("\n\n"
        "There are multiple versions of the Animation Nodes addon installed\n"
        "Please uninstall/remove all older versions of the addon\n")
    raise Exception(message)


try: from . import import_modules
except: pass

if "import_modules" not in globals():
    message = ("\n\n"
        "The Animation Nodes addon cannot be registered correctly.\n"
        "Please try to remove and install it again.\n"
        "If it still does not work, report it.\n")
    raise Exception(message)


try: import numpy
except: pass

if "numpy" not in globals():
    message = ("\n\n"
        "The Animation Nodes addon depends on the numpy library.\n"
        "Unfortunally the Blender built you are using does not have this library.\n"
        "You can either install numpy manually or use another Blender version\n"
        "that comes with numpy (e.g. the newest official Blender release).")
    raise Exception(message)


from . preferences import getBlenderVersion
if getBlenderVersion() < (2, 76, 0):
    message = ("\n\n"
        "The Animation Nodes addon requires at least Blender 2.77.\n"
        "Your are using an older version.\n"
        "Please download the latest official release.")
    raise Exception(message)


try: from . import test_compile
except: traceback.print_exc()

if "test_compile" not in globals():
    message = ("\n\n"
        "This build does not work at the moment.\n"
        "  1. Make sure that you are using compiled version of AN.\n"
        "     (Not a direct download of the repository from Github)\n"
        "  2. Check if the build you downloaded has been compiled for the OS\n"
        "     you are using. If not, download another one.\n"
        "  3. If you are on windows you can try to install a library called\n"
        "     'Visual C++ 2015 Redistributable'. Should be easy to find using\n"
        "     your search engine of choice.\n"
        "  4. It is possible that you have a build for the correct platform\n"
        "     but it still does not work. We experienced this mainly on linux.\n"
        "     Try to find another build for your platform.\n"
        "     If it still does not work, you have to compile AN yourself.\n"
        "  5. Make a bug report on Github and give as much information\n"
        "     as you can. Specifically the full error message, your OS, version, ...")
    raise Exception(message)



# Load all submodules
##################################

from . import import_modules
modules = import_modules.importAllSubmodules(__path__[0], __package__)

if "bpy" in locals():
    print("Animation Nodes can't be reloaded.")



# Initialization
##################################

from . sockets.info import updateSocketInfo
updateSocketInfo()



# register
##################################

import bpy

def register():
    bpy.utils.register_module(__name__)
    for module in modules:
        if hasattr(module, "register"):
            module.register()
    print("Registered Animation Nodes with {} modules.".format(len(modules)))

def unregister():
    bpy.utils.unregister_module(__name__)
    for module in modules:
        if hasattr(module, "unregister"):
            module.unregister()
    print("Unregistered Animation Nodes.")
