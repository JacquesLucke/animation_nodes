import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged


class CombineStringsNode(Node, AnimationNode):
	bl_idname = "CombineStringsNode"
	bl_label = "Combine Strings"
	
	def inputAmountChanged(self, context):
		self.inputs.clear()
		self.setInputSockets()
		nodeTreeChanged()
	
	inputAmount = bpy.props.IntProperty(default = 2, min = 1, soft_max = 10, update = inputAmountChanged)
	
	def init(self, context):
		self.setInputSockets()
		self.outputs.new("StringSocket", "Text")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "inputAmount", text = "Input Amount")
		
	def execute(self, input):
		output = {}
		output["Text"] = ""
		for i in range(self.inputAmount):
			output["Text"] += input[self.getInputIdentifierByIndex(i)]
		return output
		
	def setInputSockets(self):
		for i in range(self.inputAmount):
			self.inputs.new("StringSocket", "Text", self.getInputIdentifierByIndex(i))
			
	def getInputIdentifierByIndex(self, index):
		return "Text" + str(index)	
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)