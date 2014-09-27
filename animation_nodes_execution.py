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
from animation_nodes_utils import *

class AnimationNodeTree:
	def __init__(self, nodeTree):
		self.nodeTree = nodeTree
		self.nodes = {}
		for node in nodeTree.nodes:
			self.nodes[node.name] = AnimationNode(node)
			
	def execute(self):
		for node in self.nodes.values():
			node.isUpdated = False
			
		for node in self.nodes.values():
			if not node.isUpdated:
				self.updateNode(node)
				
	def updateNode(self, node):
		dependencyNames = node.getDependencyNodeNames()
		for name in dependencyNames:
			if not self.nodes[name].isUpdated:
				self.updateNode(self.nodes[name])
		node.isUpdated = True
		print(node.node.name)

class AnimationNode:
	def __init__(self, node):
		self.node = node
		self.isUpdated = False
		self.input = []
		self.output = []
		
	def getDependencyNodeNames(self):
		node = self.node
		dependencies = []
		for input in node.inputs:
			if input.is_linked: dependencies.append(input.links[0].from_node.name)
		return dependencies
		
	
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
		layout = self.layout
		execute = layout.operator("animation_nodes.execute_node_tree")
		execute.nodeTreeName = getAnimationNodeTrees()[0].name

class ExecuteNodeTree(bpy.types.Operator):
	bl_idname = "animation_nodes.execute_node_tree"
	bl_label = "Execute Node Tree"
	
	nodeTreeName = bpy.props.StringProperty()
			
	def execute(self, context):
		nodeTree = bpy.data.node_groups.get(self.nodeTreeName)
		if nodeTree is None: return {'FINISHED'}
		
		animationNodeTree = AnimationNodeTree(nodeTree)
		animationNodeTree.execute()
		print()
		
		return {'FINISHED'}		

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)