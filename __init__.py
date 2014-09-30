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
from bpy.types import NodeTree, Node, NodeSocket
from fnmatch import fnmatch
currentPath = os.path.dirname(__file__)

bl_info = {
	"name":        "Monodes",
	"description": "Node system for more flexible animations.",
	"author":      "Jacques Lucke",
	"version":     (0, 0, 1),
	"blender":     (2, 7, 2),
	"location":    "Node Editor",
	"category":    "Animation",
	"warning":	   "alpha"
	}
	
# import all modules in subDirectory
####################################

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
	
	
# register
##################################

def registerIfPossible(moduleName):
	exec("global module; module = " + moduleName)
	if hasattr(module, "register"):
		module.register()
		
def unregisterIfPossible(moduleName):
	exec("global module; module = " + moduleName)
	if hasattr(module, "unregister"):
		module.unregister()

def register():
	for moduleName in moduleNames:
		registerIfPossible(moduleName)

def unregister():
	for moduleName in moduleNames:
		unregisterIfPossible(moduleName)
		
if __name__ == "__main__":
	register()