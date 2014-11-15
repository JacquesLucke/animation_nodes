import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_IntegerInputNode(Node, AnimationNode):
	bl_idname = "mn_IntegerInputNode"
	bl_label = "Integer Input"
	isDetermined = True
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_IntegerSocket", "Number")
		self.outputs.new("mn_IntegerSocket", "Number")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Number" : "number"}
	def getOutputSocketNames(self):
		return {"Number" : "number"}
		
	def execute(self, number):
		return number