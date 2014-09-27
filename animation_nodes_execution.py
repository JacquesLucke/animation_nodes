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

import bpy
from bpy.app.handlers import persistent
from animation_nodes_utils import *

class AnimationNodeTree:
	def __init__(self, nodeTree):
		self.nodeTree = nodeTree
		self.nodes = {}
		for node in nodeTree.nodes:
			if node.type != "REROUTE":
				self.nodes[node.name] = AnimationNode(node)
			
	def execute(self):
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
		dependencies = []
		for socket in node.inputs:
			if isSocketLinked(socket): dependencies.append(getOriginSocket(socket).node.name)
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
	updateAll(bpy.context.scene)
		
@persistent
def updateAll(scene):
	nodeTrees = getAnimationNodeTrees()
	for nodeTree in nodeTrees:		
		animationNodeTree = AnimationNodeTree(nodeTree)
		animationNodeTree.execute()
	
bpy.app.handlers.frame_change_post.append(updateAll)
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)