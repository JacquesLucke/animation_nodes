import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *


class mn_TextBlock(Node, AnimationNode):
	bl_idname = "mn_TextBlock"
	bl_label = "Text Block"
	outputUseParameterName = "useOutput"
	
	selectedTextBlockName = bpy.props.StringProperty(name = "Text Block")
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_StringSocket", "Text")
		self.outputs.new("mn_StringListSocket", "Lines")
		allowCompiling()
	
	def draw_buttons(self, context, layout):
		layout.prop_search(self, "selectedTextBlockName",  bpy.data, "texts", icon="NONE", text = "")
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Text" : "text",
				"Lines" : "lines"}

	def execute(self, useOutput):
		textBlock = bpy.data.texts.get(self.selectedTextBlockName)
		
		text = ""
		if textBlock is not None:
			text = textBlock.as_string()
			
		if useOutput["Lines"]: return text, text.split("\n")
		else: return text, []
		