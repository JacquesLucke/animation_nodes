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
from mn_node_helper import AnimationNode
from mn_utils import *
from mn_execution import nodePropertyChanged, nodeTreeChanged

		
class StringLengthNode(Node, AnimationNode):
	bl_idname = "StringLengthNode"
	bl_label = "Text Length"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Text")
		self.outputs.new("IntegerSocket", "Length")
		
	def execute(self, input):
		output = {}
		output["Length"] = len(input["Text"])
		return output
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)