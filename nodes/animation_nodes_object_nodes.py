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


import bpy, math
from bpy.types import NodeTree, Node, NodeSocket
from animation_nodes_node_helper import AnimationNode
from animation_nodes_utils import *
from animation_nodes_execution import updateHandler


class ObjectInfoNode(Node, AnimationNode):
	bl_idname = "ObjectInfoNode"
	bl_label = "Object Info"
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.outputs.new("VectorSocket", "Location")
		self.outputs.new("VectorSocket", "Rotation")
		self.outputs.new("VectorSocket", "Scale")
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		output = {}
		
		output["Location"] = (0, 0, 0)
		output["Rotation"] = (0, 0, 0)
		output["Scale"] = (1, 1, 1)
		
		if object is None:
			return output
			
		output["Location"] = object.location
		output["Rotation"] = object.rotation_euler
		output["Scale"] = object.scale
		
		return output
		
class ObjectOutputNode(Node, AnimationNode):
	bl_idname = "ObjectOutputNode"
	bl_label = "Object Output"
	
	useLocation = bpy.props.BoolVectorProperty(update = updateHandler)
	useRotation = bpy.props.BoolVectorProperty(update = updateHandler)
	useScale = bpy.props.BoolVectorProperty(update = updateHandler)
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("VectorSocket", "Location")
		self.inputs.new("VectorSocket", "Rotation")
		self.inputs.new("VectorSocket", "Scale").vector = (1, 1, 1)
		
	def draw_buttons(self, context, layout):
		col = layout.column(align = True)
		
		row = col.row(align = True)
		row.label("Use Location")
		row.prop(self, "useLocation", index = 0, text = "X")
		row.prop(self, "useLocation", index = 1, text = "Y")
		row.prop(self, "useLocation", index = 2, text = "Z")
		row = col.row(align = True)
		row.label("Use Rotation")
		row.prop(self, "useRotation", index = 0, text = "X")
		row.prop(self, "useRotation", index = 1, text = "Y")
		row.prop(self, "useRotation", index = 2, text = "Z")
		row = col.row(align = True)
		row.label("Use Scale")
		row.prop(self, "useScale", index = 0, text = "X")
		row.prop(self, "useScale", index = 1, text = "Y")
		row.prop(self, "useScale", index = 2, text = "Z")
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		if object is None:
			return {}
		
		if self.useLocation[0]: object.location[0] = input["Location"][0]
		if self.useLocation[1]: object.location[1] = input["Location"][1]
		if self.useLocation[2]: object.location[2] = input["Location"][2]
		
		if self.useRotation[0]: object.rotation_euler[0] = input["Rotation"][0]
		if self.useRotation[1]: object.rotation_euler[1] = input["Rotation"][1]
		if self.useRotation[2]: object.rotation_euler[2] = input["Rotation"][2]
		
		if self.useScale[0]: object.scale[0] = input["Scale"][0]
		if self.useScale[1]: object.scale[1] = input["Scale"][1]
		if self.useScale[2]: object.scale[2] = input["Scale"][2]
		
		return {}
		
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)