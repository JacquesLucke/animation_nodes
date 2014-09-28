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

		
class ToStringConversion(Node, AnimationNode):
	bl_idname = "ToStringConversion"
	bl_label = "To String"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("StringSocket", "Text")
		
	def execute(self, input):
		output = {}
		output["Text"] = str(input["Value"])
		return output
		
class ToFloatConversion(Node, AnimationNode):
	bl_idname = "ToFloatConversion"
	bl_label = "To Float"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("FloatSocket", "Number")
		
	def execute(self, input):
		output = {}
		output["Number"] = str(input["Value"])
		return output
		
class ToIntegerConversion(Node, AnimationNode):
	bl_idname = "ToIntegerConversion"
	bl_label = "To Integer"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Value")
		self.outputs.new("IntegerSocket", "Number")
		
	def execute(self, input):
		output = {}
		output["Number"] = int(input["Value"])
		return output
		
class CombineVector(Node, AnimationNode):
	bl_idname = "CombineVector"
	bl_label = "Combine Vector"
	
	def init(self, context):
		self.inputs.new("FloatSocket", "X")
		self.inputs.new("FloatSocket", "Y")
		self.inputs.new("FloatSocket", "Z")
		self.outputs.new("VectorSocket", "Vector")
		
	def execute(self, input):
		output = {}
		output["Vector"] = (input["X"], input["Y"], input["Z"])
		return output
	
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)