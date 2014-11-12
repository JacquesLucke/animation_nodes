import bpy
from mathutils import Vector
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_VectorDistanceNode(Node, AnimationNode):
	bl_idname = "mn_VectorDistanceNode"
	bl_label = "Vector Distance"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorSocket", "A")
		self.inputs.new("mn_VectorSocket", "B")
		self.outputs.new("mn_FloatSocket", "Distance")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"A" : "a", "B" : "b"}
	def getOutputSocketNames(self):
		return {"Distance" : "distance"}
		
	def execute(self, a, b):
		return (Vector(a) - Vector(b)).length