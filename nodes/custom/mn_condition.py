import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class condition(Node, AnimationNode):
	bl_idname = "ConditionNode"
	bl_label = "Simple A>B condition"
	
	def init(self, context):
		
		self.inputs.new("FloatSocket", "A").number = 0.0
		self.inputs.new("FloatSocket", "B").number = 1.0

		self.inputs.new("ObjectSocket", "Object A > B")
		self.inputs.new("ObjectSocket", "Object B > A")

		self.inputs.new("StringSocket", "Text A > B")
		self.inputs.new("StringSocket", "Text B > A")

		self.inputs.new("FloatSocket", "Number A > B")
		self.inputs.new("FloatSocket", "Number B > A")

		self.outputs.new("ObjectSocket", "Output object")
		self.outputs.new("StringSocket", "Output text")
		self.outputs.new("FloatSocket", "Output number")

		
	def execute(self, input):
		output = {}
		A_value = input["A"]
		B_value = input["B"]

		if A_value > B_value:
			output["Output object"] = input["Object A > B"]
			output["Output text"] = input["Text A > B"]
			output["Output number"] = input["Number A > B"]
		else:
			output["Output object"] = input["Object B > A"]
			output["Output text"] = input["Text B > A"]
			output["Output number"] = input["Number B > A"]

		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)