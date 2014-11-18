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

import bpy, sys, os
import importlib
from nodeitems_utils import register_node_categories, unregister_node_categories
from bpy.types import NodeTree, Node, NodeSocket
from fnmatch import fnmatch
from bpy.props import *
currentPath = os.path.dirname(__file__)

bl_info = {
    "name":        "Animation Nodes",
    "description": "Node system for more flexible animations.",
    "author":      "Jacques Lucke",
    "version":     (0, 0, 1),
    "blender":     (2, 7, 2),
    "location":    "Node Editor",
    "category":    "Animation",
    "warning":     "alpha"
    }
    
# import all modules in same/subdirectories
###########################################

if __name__ != "animation_nodes":
    sys.modules["animation_nodes"] = sys.modules[__name__]

def getAllImportFiles():
    # an_dir name of a
    _, animation_nodes_dir = os.path.split(currentPath)
    for root, dirs, files in os.walk(currentPath):
        base, tail = os.path.split(root)
        curr_dir = [tail]
        while  animation_nodes_dir != tail:
            base, tail = os.path.split(base)
            curr_dir.append(tail)
        curr_dir = curr_dir[:-1]
        if curr_dir:
            i_path = "animation_nodes." + ".".join(curr_dir[::-1])
        else:
            i_path = "animation_nodes"
        for f in filter(lambda f:fnmatch(f,"*.py"), files):
            if not f[:-3] == "__init__":
                yield (f[:-3], i_path)

animation_nodes_modules = []

for name, base in getAllImportFiles():
    print("importing", name, base)
    mod = importlib.import_module("{}.{}".format(base,name))
    animation_nodes_modules.append(mod)

from animation_nodes.mn_execution import nodeTreeChanged
class GlobalUpdateSettings(bpy.types.PropertyGroup):
    frameChange = BoolProperty(default = True, name = "Frame Change")
    sceneUpdate = BoolProperty(default = True, name = "Scene Update")
    propertyChange = BoolProperty(default = True, name = "Property Change")
    treeChange = BoolProperty(default = True, name = "Tree Change")
    skipFramesAmount = IntProperty(default = 0, name = "Skip Frames", min = 0, soft_max = 10)
    
class DeveloperSettings(bpy.types.PropertyGroup):
    printUpdateTime = BoolProperty(default = False, name = "Print Global Update Time")
    printGenerationTime = BoolProperty(default = False, name = "Print Script Generation Time")
    executionProfiling = BoolProperty(default = False, name = "Node Execution Profiling", update = nodeTreeChanged)

import animation_nodes.mn_keyframes
class Keyframes(bpy.types.PropertyGroup):
    name = StringProperty(default = "", name = "Keyframe Name")
    type = EnumProperty(items = mn_keyframes.getKeyframeTypeItems(), name = "Keyframe Type")
    
class KeyframesSettings(bpy.types.PropertyGroup):
    keys = CollectionProperty(type = Keyframes, name = "Keyframes")
    selectedPath = StringProperty(default = "", name = "Selected Path")
    selectedName = EnumProperty(items = mn_keyframes.getKeyframeNameItems, name = "Keyframe Name")
    newName = StringProperty(default = "", name = "Name")
    selectedType = EnumProperty(items = mn_keyframes.getKeyframeTypeItems(), name = "Keyframe Type")
    
class AnimationNodesSettings(bpy.types.PropertyGroup):
    update = PointerProperty(type = GlobalUpdateSettings, name = "Update Settings")
    developer = PointerProperty(type = DeveloperSettings, name = "Developer Settings")
    keyframes = PointerProperty(type = KeyframesSettings, name = "Keyframes")
    
    
    
    
# register
##################################

def unregisterIfPossible(moduleName):
    bpy.utils.unregister_module(moduleName)
    
def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.mn_settings = PointerProperty(type = AnimationNodesSettings, name = "Animation Node Settings")

    for module in animation_nodes_modules:
        if hasattr(module, "register"):
            try:
                module.register()
            except:
                print(module.__name__)
    categories = mn_node_register.getNodeCategories()
    register_node_categories("ANIMATIONNODES", categories)
    
    bpy.types.Scene.mn_settings = PointerProperty(type = AnimationNodesSettings, name = "Animation Node Settings")

def unregister():
    for module in reversed(animation_nodes_modules):
        if hasattr(module, "register"):
            module.register()
    bpy.utils.unregister_module(__name__)
    
    unregister_node_categories("ANIMATIONNODES")
        
if __name__ == "__main__":
    register()
