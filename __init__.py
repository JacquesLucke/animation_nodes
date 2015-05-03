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

 
import importlib, sys, os
from nodeitems_utils import register_node_categories, unregister_node_categories
import nodeitems_utils
from bpy.types import NodeTree, Node, NodeSocket
from fnmatch import fnmatch
from bpy.props import *

bl_info = {
	"name":        "Animation Nodes",
	"description": "Node system for more flexible animations.",
	"author":      "Jacques Lucke",
	"version":     (0, 0, 1),
	"blender":     (2, 7, 2),
	"location":    "Node Editor",
	"category":    "Node",
	"warning":     "alpha"
	}
	
# import all modules in same/subdirectories
###########################################
currentPath = os.path.dirname(__file__)

if __name__ != "animation_nodes":
	sys.modules["animation_nodes"] = sys.modules[__name__]

def getAllImportFiles():
	"""
	Should return full python import path to module as
	animation_nodes.nodes.mesh.mn_mesh_polygon_info
	animation_nodes.sockets.mn_float_socket
	"""
	def get_path(base):
		b, t = os.path.split(base)
		if __name__ == t:
			return ["animation_nodes"]
		else:
			return get_path(b) + [t]

	for root, dirs, files in os.walk(currentPath):
		path = ".".join(get_path(root))
		for f in filter(lambda f:f.endswith(".py"), files):
			name = f[:-3]
			if not name == "__init__":
				yield path + "." + name

animation_nodes_modules = []

for name in getAllImportFiles():
	mod = importlib.import_module(name)
	animation_nodes_modules.append(mod)

reload_event = "bpy" in locals()

import bpy

from animation_nodes.mn_execution import nodeTreeChanged
class GlobalUpdateSettings(bpy.types.PropertyGroup):
	frameChange = BoolProperty(default = True, name = "Frame Change", description = "Recalculate the nodes when the frame has been changed")
	sceneUpdate = BoolProperty(default = True, name = "Scene Update", description = "Recalculate the nodes continuously")
	propertyChange = BoolProperty(default = True, name = "Property Change", description = "Recalculate the nodes when a property of a node changed")
	treeChange = BoolProperty(default = True, name = "Tree Change")
	skipFramesAmount = IntProperty(default = 0, name = "Skip Frames", min = 0, soft_max = 10, description = "Only recalculate the nodes every nth frame")
	redrawViewport = BoolProperty(default = True, name = "Redraw Viewport", description = "Redraw the UI after each execution. Turning it off gives a better performance but worse realtime feedback.")
	resetCompileBlockerWhileRendering = BoolProperty(default = True, name = "Force Update While Rendering", description = "Force the node tree to execute if the frame changes and Blender is rendering currently (nodes which change the frame may lock the UI)")
	
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
	

#  Reload
#  makes F8 reload actually reload the code

if reload_event:
	for module in animation_nodes_modules:
		importlib.reload(module)
	
# register
##################################

def register():
	#  two calls needed
	#  one for registering the things in this file
	#  the other everything that lives in the fake 'animation_nodes'
	#  namespace. It registers everything else.
	bpy.utils.register_module(__name__)
	bpy.utils.register_module("animation_nodes")

	categories = mn_node_register.getNodeCategories()
	# if we use F8 reload this happens.
	if "ANIMATIONNODES" in nodeitems_utils._node_categories:
		unregister_node_categories("ANIMATIONNODES")
	register_node_categories("ANIMATIONNODES", categories)
	
	bpy.types.Scene.mn_settings = PointerProperty(type = AnimationNodesSettings, name = "Animation Node Settings")
	print("Loaded Animation Nodes with {} modules".format(len(animation_nodes_modules)))

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.utils.unregister_module("animation_nodes")
	
	unregister_node_categories("ANIMATIONNODES")
		
if __name__ == "__main__":
	register()
