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
from animation_nodes_execution import updateHandler


class ObjectInfoNode(Node, AnimationNode):
	bl_idname = "ObjectInfoNode"
	bl_label = "Object Info"
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.outputs.new("VectorSocket", "Location")
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		output = {}
		output["Location"] = (0, 0, 0)
		if object is None:
			return output
		output["Location"] = object.location
		return output
		
	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)