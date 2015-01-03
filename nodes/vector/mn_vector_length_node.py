import bpy
import mathutils
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_VectorLengthNode(Node, AnimationNode):
	bl_idname = "mn_VectorLengthNode"
	bl_label = "Vector Length"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorSocket", "Vector")
		self.outputs.new("mn_FloatSocket", "Length")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Vector" : "vector"}
	def getOutputSocketNames(self):
		return {"Length" : "length"}
		
	def execute(self, vector):
		return vector.length

