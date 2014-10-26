import bpy, bmesh
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *

class mn_ObjectInfoNode(Node, AnimationNode):
	bl_idname = "mn_input_vertices"
	bl_label = "Input Object vertices"
	node_category = "object"

	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object")
		self.inputs.new("mn_IntegerSocket", "Index")
		self.inputs.new("mn_FloatSocket", "x")
		self.inputs.new("mn_FloatSocket", "y")
		self.inputs.new("mn_FloatSocket", "z")
		
		allowCompiling()

	def execute(self, input):
		output = {}
		i = input["Index"]
		obj = input["Object"]
		x = input["x"]
		y = input["y"]
		z = input["z"]
		vert = obj.data.vertices

		obj.data.vertices[i].co = [x,y,z]

