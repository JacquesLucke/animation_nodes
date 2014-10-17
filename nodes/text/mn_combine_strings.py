import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_utils import *


class mn_CombineStringsNode(Node, AnimationNode):
	bl_idname = "mn_CombineStringsNode"
	bl_label = "Combine Strings"
	
	def inputAmountChanged(self, context):
		forbidCompiling()
		connections = getConnectionDictionaries(self)
		self.inputs.clear()
		self.setInputSockets()
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
		nodeTreeChanged()
	
	inputAmount = bpy.props.IntProperty(default = 2, min = 1, soft_max = 10, update = inputAmountChanged)
	
	def init(self, context):
		forbidCompiling()
		self.setInputSockets()
		self.outputs.new("mn_StringSocket", "Text")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "inputAmount", text = "Input Amount")
		
	def execute(self, input):
		output = {}
		output["Text"] = ""
		for i in range(self.inputAmount):
			output["Text"] += input[self.getInputNameByIndex(i)]
		return output
		
	def setInputSockets(self):
		for i in range(self.inputAmount):
			self.inputs.new("mn_StringSocket", self.getInputNameByIndex(i))
			
	def getInputNameByIndex(self, index):
		return "Text " + str(index)	