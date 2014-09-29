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
from animation_nodes_node_helper import AnimationNode
from animation_nodes_utils import *
from animation_nodes_execution import nodePropertyChanged


class FloatMathNode(Node, AnimationNode):
	bl_idname = "FloatMathNode"
	bl_label = "Math (Float)"
	
	mathTypes = [
		("ADD", "Add", ""),
		("SUBTRACT", "Subtract", ""),
		("MULITPLY", "Multiply", ""),
		("DIVIDE", "Divide", ""),
		("MODULO", "Modulo", "")]
	mathTypesProperty = bpy.props.EnumProperty(name = "Type", items = mathTypes, default = "ADD", update = nodePropertyChanged)
	
	def init(self, context):
		self.inputs.new("FloatSocket", "A")
		self.inputs.new("FloatSocket", "B")
		self.outputs.new("FloatSocket", "Result")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "mathTypesProperty")
		
	def execute(self, input):
		a = input["A"]
		b = input["B"]
		result = 0
		type = self.mathTypesProperty
		try:
			if type == "ADD": result = a + b
			elif type == "SUBTRACT": result = a - b
			elif type == "MULITPLY": result = a * b
			elif type == "DIVIDE": result = a / b
			elif type == "MODULO": result = a % b
		except (ZeroDivisionError):
			print("ZeroDivisionError - " + self.name)
		output = {}
		output["Result"] = result
		return output
		
class ExpressionNode(Node, AnimationNode):
	bl_idname = "ExpressionNode"
	bl_label = "Expression"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Expression").string = "a+b"
		self.inputs.new("GenericSocket", "a")
		self.inputs.new("GenericSocket", "b")
		self.outputs.new("GenericSocket", "Result")
		
	def execute(self, input):
		a = input["a"]
		b = input["b"]
		expression = input["Expression"]
		result = 0
		try:
			result = eval(expression)
		except (ZeroDivisionError):
			print("expression error - " + self.name)
		output = {}
		output["Result"] = result
		return output
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)