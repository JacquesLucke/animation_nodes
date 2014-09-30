import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class SubstringNode(Node, AnimationNode):
	bl_idname = "SubstringNode"
	bl_label = "Substrings"
	
	ignoreLength =  bpy.props.BoolProperty(default = False, update = nodePropertyChanged)
	
	def init(self, context):
		self.inputs.new("StringSocket", "Text")
		self.inputs.new("IntegerSocket", "Start").number = 0
		self.inputs.new("IntegerSocket", "Length").number = 5
		self.outputs.new("StringSocket", "Text")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "ignoreLength", text = "Ignore Length")
		
	def execute(self, input):
		output = {}
		output["Text"] = input["Text"][ max(input["Start"],0):]
		if not self.ignoreLength:
			output["Text"] = output["Text"][:max(input["Length"],0) ]
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)