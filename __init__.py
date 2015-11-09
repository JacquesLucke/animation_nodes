'''
Copyright (C) 2014 Jacques Lucke
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
    "version":     (1, 0, 1),
    "blender":     (2, 7, 6),
    "location":    "Node Editor",
    "category":    "Node",
    "warning":     ""
    }



# load and reload submodules
##################################

import importlib
from . import developer_utils
importlib.reload(developer_utils)
modules = developer_utils.setup_addon_modules(__path__, __name__, "bpy" in locals())



# Public API
##################################

from . execution import units
subprogramsByName = units.getSubprogramUnitsByName
setup = units.setupExecutionUnits
finish = units.finishExecutionUnits



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
