'''
Copyright (C) 2016 Jacques Lucke
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
    "name":        "Animation Nodes Fork",
    "description": "Node based visual scripting system designed for motion graphics in Blender.",
    "author":      "Jacques Lucke_Jared Webber",
    "version":     (1, 6, 1),
    "blender":     (2, 77, 0),
    "location":    "Node Editor",
    "category":    "Node",
    "warning":     ""
    }



# Test Environment
##################################

try: from . import developer_utils
except: pass

if "developer_utils" not in globals():
    message = ("\n\n"
        "The Animation Nodes addon cannot be registered correctly\n"
        "Troubleshooting:\n"
        "  1. Try installing the addon in the newest official Blender version.\n"
        "  2. Try installing the newest Animation Nodes version from Github.\n"
        "  3. Go into the addons directory of Blender and rename the folder "
             "'animation_nodes-###' to only 'animation_nodes'.\n"
        "  4. Check that the 'animation_nodes' folder contains the __init__.py file.\n"
        "  5. Enable 'Auto Run Python Scripts' in the User Preferences.\n"
        "  6. If nothing else works report this error on Github or in the Forum.")
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



# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# Initialization
##################################

from . sockets.info import updateSocketInfo
updateSocketInfo()



# register
##################################

import bpy
from . register_files import registerFiles
from . register_files import unregisterFiles

def register():
    bpy.utils.register_module(__name__)
    registerFiles()
    print("Registered Animation Nodes with {} modules.".format(len(modules)))

def unregister():
    bpy.utils.unregister_module(__name__)
    unregisterFiles()
    print("Unregistered Animation Nodes")
