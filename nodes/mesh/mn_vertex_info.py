import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.utils.mn_mesh_utils import *

class mn_VertexInfo(Node, AnimationNode):
	bl_idname = "mn_VertexInfo"
	bl_label = "Vertex Info"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VertexSocket", "Vertex")
		self.outputs.new("mn_VectorSocket", "Location")
		self.outputs.new("mn_VectorSocket", "Normal")
		self.outputs.new("mn_FloatListSocket", "Group Weights")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Vertex" : "vertex"}
	def getOutputSocketNames(self):
		return {"Location" : "location",
				"Normal" : "normal",
				"Group Weights" : "groupWeights"}
		
	def execute(self, vertex):
		return vertex.location, vertex.normal, vertex.groupWeights