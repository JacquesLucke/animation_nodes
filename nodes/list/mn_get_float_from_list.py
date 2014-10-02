import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class GetFloatFromFloatListNode(Node, AnimationNode):
	bl_idname = "GetFloatFromFloatListNode"
	bl_label = "Get Float"
	
	clampIndex = bpy.props.BoolProperty(default = True)
	
	def init(self, context):
		self.inputs.new("FloatListSocket", "List")
		self.inputs.new("IntegerSocket", "Index")
		self.outputs.new("FloatSocket", "Number")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "clampIndex", text = "Clamp Index")
		
	def execute(self, input):
		output = {}
		list = input["List"]
		index = input["Index"]
		output["Number"] = 0
		if len(list) > 0:
			output["Number"] = list[max(min(index, len(list) - 1), 0)]
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)