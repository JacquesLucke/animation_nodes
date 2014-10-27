import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_DebugVectorOutputNode(Node, AnimationNode):
	bl_idname = "mn_DebugVectorOutputNode"
	bl_label = "Debug Vector Output"
	
	printDebugString = bpy.props.BoolProperty(default = False)
	debugOutputString_component0 = bpy.props.StringProperty(default = "")
	debugOutputString_component1 = bpy.props.StringProperty(default = "")
	debugOutputString_component2 = bpy.props.StringProperty(default = "")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorSocket", "Vector")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "printDebugString", text = "Print")
		layout.label(self.debugOutputString_component0)
		layout.label(self.debugOutputString_component1)
		layout.label(self.debugOutputString_component2)
		
	def execute(self, input):
		self.debugOutputString_component0 = str(round(input["Data"][0], 2))
		self.debugOutputString_component1 = str(round(input["Data"][1], 2))
		self.debugOutputString_component2 = str(round(input["Data"][2], 2))
		return {}
