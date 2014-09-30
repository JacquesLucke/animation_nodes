import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class ExpressionNode(Node, AnimationNode):
	bl_idname = "ExpressionNode"
	bl_label = "Expression"
	
	def init(self, context):
		self.inputs.new("StringSocket", "Expression").string = "a+b"
		self.inputs.new("GenericSocket", "a")
		self.inputs.new("GenericSocket", "b")
		self.outputs.new("GenericSocket", "Result")
		
	def execute(self, input):
		a = input["a"]
		b = input["b"]
		expression = input["Expression"]
		result = 0
		try:
			result = eval(expression)
		except (ZeroDivisionError):
			print("expression error - " + self.name)
		output = {}
		output["Result"] = result
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)