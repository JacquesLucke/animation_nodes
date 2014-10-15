import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class TemplateNode(Node, AnimationNode):
	bl_idname = "TemplateNode"
	bl_label = "Node Template"

	def init(self, context):
		forbidCompiling()
		self.inputs.new("IntegerSocket", "Amount")
		self.inputs.new("StringSocket", "Text")
		self.outputs.new("StringSocket", "New Text")
		self.outputs.new("IntegerSocket", "Length")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		pass
		
	def execute(self, input):
		output = {}
		amount = input["Amount"]
		text = input["Text"]
		output["New Text"] = amount * text
		output["Length"] = len(output["New Text"])
		return output
		
if __name__ == "__main__":
	bpy.utils.register_module(__name__)