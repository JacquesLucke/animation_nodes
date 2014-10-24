import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_GetListLengthNode(Node, AnimationNode):
	bl_idname = "mn_GetListLengthNode"
	bl_label = "Get List Length"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_GenericSocket", "List")
		self.outputs.new("mn_IntegerSocket", "Length")
		allowCompiling()
		
	def execute(self, input):
		output = {}
		try:
			output["Length"] = len(input["List"])
		except:
			output["Length"] = 0
		return output