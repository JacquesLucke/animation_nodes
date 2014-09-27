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


class CombineStringsNode(Node, AnimationNode):
	bl_idname = "CombineStringsNode"
	bl_label = "Combine Strings"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Text 1")
		self.inputs.new("StringSocket", "Text 2")
		self.outputs.new("StringSocket", "Text")
		
	def execute(self, input):
		output = {}
		output["Text"] = input["Text 1"] + input["Text 2"]
		return output
		
class ReplicateStringsNode(Node, AnimationNode):
	bl_idname = "ReplicateStringsNode"
	bl_label = "Replicate Strings"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Text")
		self.inputs.new("IntegerSocket", "Amount")
		self.outputs.new("StringSocket", "Text")
		
	def execute(self, input):
		output = {}
		output["Text"] = input["Text"] * input["Amount"]
		return output
		
class SubstringNode(Node, AnimationNode):
	bl_idname = "SubstringNode"
	bl_label = "Substrings"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Text")
		self.inputs.new("IntegerSocket", "Start")
		self.inputs.new("IntegerSocket", "Length")
		self.outputs.new("StringSocket", "Text")
		
	def execute(self, input):
		output = {}
		output["Text"] = input["Text"][ max(input["Start"],0) : max(input["Length"],0) ]
		return output
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)