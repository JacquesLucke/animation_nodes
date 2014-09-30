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
from mn_node_helper import AnimationNode
from mn_utils import *


class AttributeOutputNode(Node, AnimationNode):
	bl_idname = "AttributeOutputNode"
	bl_label = "Attribute Output"
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("StringSocket", "Attribute")
		self.inputs.new("GenericSocket", "Value")
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		attribute = input["Attribute"]
		value = input["Value"]
		try:
			exec("object." + attribute + " = value")
		except:
			print("attribute not found or wrong data type - " + attribute)
		return {}
		
class DebugOutputNode(Node, AnimationNode):
	bl_idname = "DebugOutputNode"
	bl_label = "Debug"
	
	debugOutputString = bpy.props.StringProperty(default = "")
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Data")
		
	def draw_buttons(self, context, layout):
		layout.label(self.debugOutputString)
		
	def execute(self, input):
		self.debugOutputString = str(input["Data"])
		return {}
	
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)