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
from animation_nodes_utils import *

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

class AnimationTreeCache:
	def __init__(self):
		self.dependencies = CachePerNode()
	def clear(self):
		self.dependencies.clear()
		
	def getDependencyNodeNames(self, node):
		return self.dependencies.getObjectFromNode(node)
	def setNodeDependencies(self, node, dependencies):
		self.dependencies.setObjectFromNode(node, dependencies)


animationTreeCache = AnimationTreeCache()


class AnimationNodeTree:
	def __init__(self, nodeTree):
		self.nodeTree = nodeTree
		self.nodes = {}
		for node in nodeTree.nodes:
			if node.type != "REROUTE":
				self.nodes[node.name] = AnimationNode(node)
			
	def execute(self, useDependencyCache = False):
		if not useDependencyCache:
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
		for socket in node.node.inputs:
			value = None
			if isSocketLinked(socket):
				parentNode = self.nodes[getOriginSocket(socket).node.name]
				value = parentNode.output[getOriginSocket(socket).name]
			else:
				value = socket.getValue()
			node.input[socket.name] = value
	

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
	bl_idname = "animation_nodes_panel"
	bl_label = "Animation Nodes"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_category = "Animation"
	bl_context = "objectmode"
	
	@classmethod
	def poll(self, context):
		return len(getAnimationNodeTrees()) > 0
	
	def draw(self, context):
		pass
		
def updateHandler(self, context):
	updateAnimationTrees(True)
		
@persistent
def updateAll(scene):
	updateAnimationTrees(False)
		
def updateAnimationTrees(treeChanged = True):
	start = time.clock()
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:		
		animationNodeTree = AnimationNodeTree(nodeTree)
		animationNodeTree.execute(useDependencyCache = not treeChanged)
	print(time.clock() - start)
	
bpy.app.handlers.frame_change_post.append(updateAll)
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)