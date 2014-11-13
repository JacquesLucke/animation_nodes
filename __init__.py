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
	"warning":	   "alpha"
	}
	
# import all modules in same/subdirectories
###########################################

def getAllPathsToPythonFiles(root):
	filePaths = []
	pattern = "*.py"
	for (path, subDirectory, files) in os.walk(root):
		for name in files:
			if fnmatch(name, pattern): filePaths.append(os.path.join(path, name))
	return filePaths
def getModuleNames(filePaths):
	moduleNames = []
	for filePath in filePaths:
		moduleName = os.path.basename(os.path.splitext(filePath)[0])
		if moduleName != "__init__":
			moduleNames.append(moduleName)
	return moduleNames
def getExecStringsForImport(moduleNames):
	execStrings = []
	for name in moduleNames:
		execStrings.append("import " + name)
	return execStrings
def appendPathsToPythonSearchDirectories(filePaths):
	for filePath in filePaths:
		sys.path.append(os.path.dirname(filePath))

filePaths = getAllPathsToPythonFiles(currentPath)
moduleNames = getModuleNames(filePaths)
appendPathsToPythonSearchDirectories(filePaths)
execStrings = getExecStringsForImport(moduleNames)
for name in moduleNames:
	exec("import " + name)
	print("import " + name)	

from mn_execution import nodeTreeChanged	
class GlobalUpdateSettings(bpy.types.PropertyGroup):
	frameChange = BoolProperty(default = True, name = "Frame Change")
	sceneUpdate = BoolProperty(default = True, name = "Scene Update")
	propertyChange = BoolProperty(default = True, name = "Property Change")
	skipFramesAmount = IntProperty(default = 0, name = "Skip Frames", min = 0, soft_max = 10)
	
class DeveloperSettings(bpy.types.PropertyGroup):
	printUpdateTime = BoolProperty(default = False, name = "Print Update Time")
	printGenerationTime = BoolProperty(default = False, name = "Print Script Generation Time")
	showErrors = BoolProperty(default = False, name = "Show Full Error")
	executionProfiling = BoolProperty(default = False, name = "Node Execution Profiling", update = nodeTreeChanged)

import mn_keyframes	
class Keyframes(bpy.types.PropertyGroup):
	name = StringProperty(default = "", name = "Keyframe Name")
	type = EnumProperty(items = mn_keyframes.getKeyframeTypeItems(), name = "Keyframe Type")
	
class KeyframesSettings(bpy.types.PropertyGroup):
	keys = CollectionProperty(type = Keyframes, name = "Keyframes")
	selectedPath = StringProperty(default = "", name = "Selected Path")
	
class AnimationNodesSettings(bpy.types.PropertyGroup):
	update = PointerProperty(type = GlobalUpdateSettings, name = "Update Settings")
	developer = PointerProperty(type = DeveloperSettings, name = "Developer Settings")
	keyframes = PointerProperty(type = KeyframesSettings, name = "Keyframes")
	
	
	
	
# register
##################################

def registerIfPossible(moduleName):
	try:
		bpy.utils.register_module(moduleName)
	except: pass
		
def unregisterIfPossible(moduleName):
	try:
		bpy.utils.unregister_module(moduleName)
	except: pass
	
def register():
	registerIfPossible(__name__)
	for moduleName in moduleNames:
		registerIfPossible(moduleName)
	categories = mn_node_register.getNodeCategories()
	register_node_categories("ANIMATIONNODES", categories)
	
	bpy.types.Scene.mn_settings = PointerProperty(type = AnimationNodesSettings, name = "Animation Node Settings")

def unregister():
	for moduleName in moduleNames:
		unregisterIfPossible(moduleName)
	unregister_node_categories("ANIMATIONNODES")
		
if __name__ == "__main__":
	register()