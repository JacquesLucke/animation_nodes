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
from animation_nodes_utils import *

class AnimationNode:
	@classmethod
	def poll(cls, nodeTree):
		return nodeTree == "AnimationNodeTreeType"
		
		
class TextOutputNode(Node, AnimationNode):
	bl_idname = "TextOutputNode"
	bl_label = "Text Output"
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("StringSocket", "Text")
		self.inputs.new("FloatSocket", "Size").number = 1.0
		self.inputs.new("FloatSocket", "Shear").number = 0.0
		self.inputs.new("FloatSocket", "Extrude").number = 0.1
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		textObject = None
		
		if object is not None:
			textObject = bpy.data.curves.get(object.data.name)
		
		if textObject is not None:
			textObject.body = input["Text"]
			textObject.size = input["Size"]
			textObject.shear = input["Shear"]
			textObject.extrude = input["Extrude"]
		
		output = {}
		return output
		
		

class AssignActiveObjectToNode(bpy.types.Operator):
	bl_idname = "animation_nodes.assign_active_object_to_node"
	bl_label = "Assign Active Object"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	target = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		obj = getActive()
		node = getNode(self.nodeTreeName, self.nodeName)
		setattr(node, self.target, obj.name)
		return {'FINISHED'}		

		
	
class AnimationNodesCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'AnimationNodeTreeType'
	
nodeCategories = [
	AnimationNodesCategory("INPUTNODES", "Input Nodes", items = [
		NodeItem("IntegerInputNode"),
		NodeItem("FloatInputNode"),
		NodeItem("StringInputNode"),
		NodeItem("ObjectInputNode"),
		NodeItem("TimeInfoNode")
		]),
	AnimationNodesCategory("OUTPUTNODES", "Output Nodes", items = [
		NodeItem("TextOutputNode"),
		NodeItem("AttributeOutputNode")
		]),
	AnimationNodesCategory("MODIFYSTRINGS", "Modify Strings", items = [
		NodeItem("CombineStringsNode"),
		NodeItem("ReplicateStringsNode"),
		NodeItem("SubstringNode")
		]),
	AnimationNodesCategory("CONVERTTYPES", "Convert", items = [
		NodeItem("IntToStringConversion"),
		NodeItem("FloatToStringConversion"),
		NodeItem("FloatToIntegerConversion")
		]),
	AnimationNodesCategory("MATHNODES", "Math", items = [
		NodeItem("FloatMathNode")
		])
	]
	
	
# register
################################
	
def register():
	bpy.utils.register_module(__name__)
	nodeitems_utils.register_node_categories("ANIMATIONNODES", nodeCategories)

def unregister():
	nodeitems_utils.unregister_node_categories("ANIMATIONNODES", nodeCategories)	
	bpy.utils.unregister_module(__name__)