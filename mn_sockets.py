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
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged

class GenericSocket(NodeSocket):
	bl_idname = "GenericSocket"
	bl_label = "Generic Socket"
	dataType = "Generic"
	allowedInputTypes = ["Generic", "Integer", "Float", "Vector", "String"]
	
	def draw(self, context, layout, node, text):
		layout.label(text)
			
	def draw_color(self, context, node):
		return (0.6, 0.3, 0.3, 0.7)
		
	def getValue(self):
		return 0

class IntegerSocket(NodeSocket):
	bl_idname = "IntegerSocket"
	bl_label = "Integer Socket"
	dataType = "Integer"
	allowedInputTypes = ["Integer"]
	
	number = bpy.props.IntProperty(default = 0, update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			layout.prop(self, "number", text = text)
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return (0.2, 0.2, 1, 1)
		
	def getValue(self):
		return self.number
		
class FloatSocket(NodeSocket):
	bl_idname = "FloatSocket"
	bl_label = "Float Socket"
	dataType = "Float"
	allowedInputTypes = ["Float", "Integer"]
	
	number = bpy.props.FloatProperty(default = 0.0, update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			layout.prop(self, "number", text = text)
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return (0.4, 0.4, 0.7, 1)
		
	def getValue(self):
		return self.number
		
class VectorSocket(NodeSocket):
	bl_idname = "VectorSocket"
	bl_label = "Vector Socket"
	dataType = "Vector"
	allowedInputTypes = ["Vector"]
	
	vector = bpy.props.FloatVectorProperty(default = (0, 0, 0), update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			col = layout.column(align = True)
			col.label(text)
			col.prop(self, "vector", index = 0, text = "X")
			col.prop(self, "vector", index = 1, text = "Y")
			col.prop(self, "vector", index = 2, text = "Z")
			col.separator()
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return (0.05, 0.05, 0.8, 0.7)
		
	def getValue(self):
		return self.vector
		

class StringSocket(NodeSocket):
	bl_idname = "StringSocket"
	bl_label = "String Socket"
	dataType = "String"
	allowedInputTypes = ["String", "Object"]
	
	string = bpy.props.StringProperty(default = "Text", update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			layout.prop(self, "string", text = text)
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return (1, 1, 1, 1)
		
	def getValue(self):
		return self.string
		
		
class ObjectSocket(NodeSocket):
	bl_idname = "ObjectSocket"
	bl_label = "Object Socket"
	dataType = "Object"
	allowedInputTypes = ["Object", "String"]
	
	objectName = bpy.props.StringProperty(update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			col = layout.column()
			row = col.row(align = True)
			row.prop(self, "objectName", text = "")
			selector = row.operator("mn.assign_active_object_to_socket", text = "", icon = "EYEDROPPER")
			selector.nodeTreeName = node.id_data.name
			selector.nodeName = node.name
			selector.isOutput = self.is_output
			selector.socketName = self.name
			selector.target = "objectName"
			col.separator()
		else:
			layout.label(text)
		
	def draw_color(self, context, node):
		return (0, 0, 0, 1)
		
	def getValue(self):
		return self.objectName
	
	
class AssignActiveObjectToNode(bpy.types.Operator):
	bl_idname = "mn.assign_active_object_to_socket"
	bl_label = "Assign Active Object"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
	target = bpy.props.StringProperty()
	isOutput = bpy.props.BoolProperty()
	socketName = bpy.props.StringProperty()
	
	@classmethod
	def poll(cls, context):
		return getActive() is not None
		
	def execute(self, context):
		obj = getActive()
		node = getNode(self.nodeTreeName, self.nodeName)
		socket = getSocketFromNode(node, self.isOutput, self.socketName)
		setattr(socket, self.target, obj.name)
		return {'FINISHED'}
	
	
	
	
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)