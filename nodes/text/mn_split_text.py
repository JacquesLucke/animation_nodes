import bpy, re
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *

splitTypes = [
	("Characters", "Characters", ""),
	("Words", "Words", ""),
	("Lines", "Lines", ""),
	("Custom", "Custom", "") ]

class mn_SplitText(Node, AnimationNode):
	bl_idname = "mn_SplitText"
	bl_label = "Split Text"
	
	def splitTypeChanges(self, context):
		self.setHideProperty()
	
	splitType = bpy.props.EnumProperty(name = "Split Type", items = splitTypes, update = splitTypeChanges)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_StringSocket", "Text")
		self.inputs.new("mn_StringSocket", "Split By")
		self.outputs.new("mn_StringListSocket", "Text List")
		self.outputs.new("mn_IntegerSocket", "Length")
		self.setHideProperty()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "splitType", text = "Type")
		
	def setHideProperty(self):
		self.inputs["Split By"].hide = not self.splitType == "Custom"
		
	def getInputSocketNames(self):
		return {"Text" : "text",
				"Split By" : "splitBy"}
	def getOutputSocketNames(self):
		return {"Text List" : "textList",
				"Length" : "length"}

	def execute(self, text, splitBy):
		textList = []
		if self.splitType == "Characters": textList = list(text)
		elif self.splitType == "Words": textList = text.split()
		elif self.splitType == "Lines": textList = text.split("\n")
		elif self.splitType == "Custom": textList = text.split(splitBy)
		return textList, len(textList)