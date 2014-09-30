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

import bpy, time
from bpy.app.handlers import persistent
from mn_utils import *

class CachePerNode:
	def __init__(self):
		self.objects = {}
	def clear(self):
		self.objects = {}
	def getObjectFromNode(self, node):
		treeName = node.id_data.name
		nodeName = node.name
		if treeName in self.objects:
			if nodeName in self.objects[treeName]:
				return self.objects[treeName][nodeName]
		return None
	def setObjectFromNode(self, node, object):
		treeName = node.id_data.name
		nodeName = node.name
		if treeName not in self.objects:
			self.objects[treeName] = {}
		self.objects[treeName][nodeName] = object

class CachePerSocket:
	def __init__(self):
		self.objects = {}
	def clear(self):
		self.objects = {}
		
	def getObjectFromSocket(self, socket):
		identifier = self.getSocketIdentifier(socket)
		if identifier in self.objects:
			return self.objects[identifier]
		else: return None
	def setObjectForSocket(self, socket, object):
		identifier = self.getSocketIdentifier(socket)
		self.objects[identifier] = object
		
	def getSocketIdentifier(self, socket):
		return socket.node.id_data.name + socket.node.name + socket.identifier
	

class AnimationTreeCache:
	def __init__(self):
		self.dependencies = CachePerNode()
		self.originSockets = CachePerSocket()
	def clear(self):
		self.dependencies.clear()
		self.originSockets.clear()
		
	def getDependencyNodeNames(self, node):
		return self.dependencies.getObjectFromNode(node)
	def setNodeDependencies(self, node, dependencies):
		self.dependencies.setObjectFromNode(node, dependencies)
		
	def getOriginSocket(self, socket):
		data = self.originSockets.getObjectFromSocket(socket)
		if data is None:
			return None
		(treeName, nodeName, output, socketName) = data
		node = getNode(treeName, nodeName)
		if output:
			return node.outputs[socketName]
		else:
			return node.inputs[socketName]
	def setOriginSocket(self, socket, origin):
		treeName = origin.node.id_data.name
		nodeName = origin.node.name
		output = origin.is_output
		socketName = origin.name
		self.originSockets.setObjectForSocket(socket, (treeName, nodeName, output, socketName))


animationTreeCache = AnimationTreeCache()


class AnimationNodeTree:
	def __init__(self, nodeTree):
		self.nodeTree = nodeTree
		self.nodes = {}
		for node in nodeTree.nodes:
			if node.type != "REROUTE":
				self.nodes[node.name] = AnimationNode(node)
			
	def execute(self, rebuildDependencyCache = False):
		if rebuildDependencyCache:
			animationTreeCache.clear()
			self.cleanup()
		
		for node in self.nodes.values():
			node.isUpdated = False
		
		for node in self.nodes.values():
			if not node.isUpdated:
				self.updateNode(node)
				
	def cleanup(self):
		links = self.nodeTree.links
		for link in links:
			if link.to_node.type == "REROUTE":
				continue
			if not isSocketLinked(link.to_socket):
				continue
			toSocket = link.to_socket
			fromSocket = getOriginSocket(toSocket)
			if fromSocket.dataType not in toSocket.allowedInputTypes:
				self.nodeTree.links.remove(link)
				
	def updateNode(self, node):
		dependencyNames = node.getDependencyNodeNames()
		for name in dependencyNames:
			if not self.nodes[name].isUpdated:
				self.updateNode(self.nodes[name])
		self.generateInputList(node)
		node.execute()
		node.isUpdated = True
		
	def generateInputList(self, node):
		node.input = {}
		inputSockets = node.node.inputs
		
		socketPairs = []
		for socket in inputSockets:
			origin = animationTreeCache.getOriginSocket(socket)
			if origin is None:
				origin = getOriginSocket(socket)
				animationTreeCache.setOriginSocket(socket, origin)
			socketPairs.append((socket, origin))
		
		for (socket, origin) in socketPairs:
			if isOtherOriginSocket(socket, origin):
				parentNode = self.nodes[origin.node.name]
				value = parentNode.output[origin.name]
			else:
				value = socket.getValue()
			node.input[socket.identifier] = value
	

class AnimationNode:
	def __init__(self, node):
		self.node = node
		self.isUpdated = False
		self.input = {}
		self.output = {}
		
	def getDependencyNodeNames(self):
		node = self.node
		cache = animationTreeCache.getDependencyNodeNames(node)
		if cache is not None:
			return cache
		dependencies = []
		for socket in node.inputs:
			if isSocketLinked(socket): dependencies.append(getOriginSocket(socket).node.name)
		animationTreeCache.setNodeDependencies(node, dependencies)
		return dependencies
		
	def execute(self):
		self.output = self.node.execute(self.input)
		

class AnimationNodesPanel(bpy.types.Panel):
	bl_idname = "mn.panel"
	bl_label = "Monodes"
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return len(getAnimationNodeTrees()) > 0
	
	def draw(self, context):
		layout = self.layout
		layout.operator("mn.force_full_update")
		
		
class ForceNodeTreeUpdate(bpy.types.Operator):
	bl_idname = "mn.force_full_update"
	bl_label = "Force Node Tree Update"

	def execute(self, context):
		updateAnimationTrees(treeChanged = True)
		return {'FINISHED'}
		
		
def nodePropertyChanged(self, context):
	updateAnimationTrees(False)
def nodeTreeChanged():
	updateAnimationTrees(True)
		
@persistent
def updateAll(scene):
	updateAnimationTrees(False)
		
def updateAnimationTrees(treeChanged = True):
	try:
		if treeChanged: updateAndRebuildCache()
		else: fastUpdateUsingCache()
	except:
		if not treeChanged:
			try:
				updateAndRebuildCache()
			except BaseException as e:
				print("couldn't update")
				print(str(e))
			
def fastUpdateUsingCache():
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:		
		animationNodeTree = AnimationNodeTree(nodeTree)
		animationNodeTree.execute(rebuildDependencyCache = False)
		
def updateAndRebuildCache():
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:		
		animationNodeTree = AnimationNodeTree(nodeTree)
		animationNodeTree.execute(rebuildDependencyCache = True)
		
def getAnimationNodeTrees():
	nodeTrees = []
	for nodeTree in bpy.data.node_groups:
		if hasattr(nodeTree, "isAnimationNodeTree"):
			nodeTrees.append(nodeTree)
	return nodeTrees

def getNode(treeName, nodeName):
	return bpy.data.node_groups[treeName].nodes[nodeName]
def getSocketFromNode(node, isOutputSocket, name):
	if isOutputSocket:
		return node.outputs.get(name)
	else:
		return node.inputs.get(name)

	
bpy.app.handlers.frame_change_post.append(updateAll)
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)