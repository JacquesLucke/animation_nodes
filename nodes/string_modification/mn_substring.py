import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_SubstringNode(Node, AnimationNode):
	bl_idname = "mn_SubstringNode"
	bl_label = "Substrings"
	
	ignoreLength =  bpy.props.BoolProperty(default = False, update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("StringSocket", "Text")
		self.inputs.new("IntegerSocket", "Start").number = 0
		self.inputs.new("IntegerSocket", "Length").number = 5
		self.outputs.new("StringSocket", "Text")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "ignoreLength", text = "Ignore Length")
		
	def execute(self, input):
		output = {}
		output["Text"] = input["Text"][ max(input["Start"],0):]
		if not self.ignoreLength:
			output["Text"] = output["Text"][:max(input["Length"],0) ]
		return output