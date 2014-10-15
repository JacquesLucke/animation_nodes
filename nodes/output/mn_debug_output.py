import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class DebugOutputNode(Node, AnimationNode):
	bl_idname = "DebugOutputNode"
	bl_label = "Debug"
	
	printDebugString = bpy.props.BoolProperty(default = False)
	debugOutputString = bpy.props.StringProperty(default = "")
	
	def init(self, context):
		self.inputs.new("GenericSocket", "Data")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "printDebugString", text = "Print")
		layout.label(self.debugOutputString)
		
	def execute(self, input):
		self.debugOutputString = str(input["Data"])
		if self.printDebugString: print(self.debugOutputString)
		return {}