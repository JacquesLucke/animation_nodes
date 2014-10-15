import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class GetListLengthNode(Node, AnimationNode):
	bl_idname = "GetListLengthNode"
	bl_label = "Get List Length"
	
	def init(self, context):
		self.inputs.new("GenericSocket", "List")
		self.outputs.new("IntegerSocket", "Length")
		
	def execute(self, input):
		output = {}
		try:
			output["Length"] = len(input["List"])
		except:
			output["Length"] = 0
		return output