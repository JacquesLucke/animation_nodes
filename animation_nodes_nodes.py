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

import bpy, nodeitems_utils
from bpy.types import NodeTree, Node, NodeSocket
from nodeitems_utils import NodeCategory, NodeItem

class AnimationNode:
	@classmethod
	def poll(cls, nodeTree):
		return nodeTree == "AnimationNodeTreeType"
		
class StringInputNode(Node, AnimationNode):
	bl_idname = "StringInputNode"
	bl_label = "String Input"
	
	stringProperty = bpy.props.StringProperty(default = "Hello World")
	
	def init(self, context):
		self.outputs.new("NodeSocketString", "Text")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "stringProperty", text = "")
	
class AnimationNodesCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'AnimationNodeTreeType'
	
nodeCategories = [
	AnimationNodesCategory("INPUTNODES", "Input Nodes", items = [
		NodeItem("StringInputNode", label = "String Input")
		])
	]
	
	
def register():
	bpy.utils.register_module(__name__)
	nodeitems_utils.register_node_categories("ANIMATIONNODES", nodeCategories)

def unregister():
	nodeitems_utils.unregister_node_categories("ANIMATIONNODES", nodeCategories)
	
	bpy.utils.unregister_module(__name__)