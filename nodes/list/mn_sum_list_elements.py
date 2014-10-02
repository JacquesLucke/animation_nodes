import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class SumFloatListElementsNode(Node, AnimationNode):
	bl_idname = "SumFloatListElementsNode"
	bl_label = "Sum Floats"
	
	def init(self, context):
		self.inputs.new("FloatListSocket", "List")
		self.inputs.new("IntegerSocket", "Start")
		self.inputs.new("IntegerSocket", "End")
		self.outputs.new("FloatSocket", "Sum")
		
	def execute(self, input):
		output = {}
		list = input["List"]
		
		start = clampInt(input["Start"], 0, len(list))
		end = clampInt(input["End"], 0, len(list))
		
		output["Sum"] = 0.0
		for i in range(start, end):
			output["Sum"] += list[i]
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)