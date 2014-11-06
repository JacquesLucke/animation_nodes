import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *


class mn_TextBlock(Node, AnimationNode):
	bl_idname = "mn_TextBlock"
	bl_label = "Text Block"
	
	selectedTextBlockName = bpy.props.StringProperty(name = "Text Block")
	
	def init(self, context):
		forbidCompiling()
		self.outputs.new("mn_StringSocket", "Text")
		allowCompiling()
	
	def draw_buttons(self, context, layout):
		layout.prop_search(self, "selectedTextBlockName",  bpy.data, "texts", icon="NONE", text = "")
		
	def getInputSocketNames(self):
		return {}
	def getOutputSocketNames(self):
		return {"Text" : "text"}

	def execute(self):
		textBlock = bpy.data.texts.get(self.selectedTextBlockName)
		
		if textBlock is None:
			return ""
		else:
			return textBlock.as_string()