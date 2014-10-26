import bpy, bmesh
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *

class mn_ObjectInfoNode(Node, AnimationNode):
	bl_idname = "mn_object_vertices"
	bl_label = "Object vertices"
	node_category = "object"

	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object")
		self.inputs.new("mn_IntegerSocket", "Index")
		self.outputs.new("mn_VectorSocket", "Output")
		allowCompiling()

	def execute(self, input):
		output = {}
		i = input["Index"]
		obj = input["Object"]
		vert = obj.data.vertices
		
		if obj is None:
			return output

		if i < 0:
			return output
		
		if i > len(vert):
			return output
		
		output["Output"] = obj.matrix_world * vert[i].co
		return output

