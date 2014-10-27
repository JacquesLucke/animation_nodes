import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling

def updateNode(node, context):
	nodeTreeChanged()

class mn_FloatCompareNode(Node, AnimationNode):
	bl_idname = "mn_FloatCompareNode"
	bl_label = "Compare Numbers"

	
	comparisonTypes = [
		("SMALLER_EQ", "Smaller or equal", ""),
		("SMALLER", "Smaller", ""),
		("GREATER_EQ", "Greater or equal", ""),
		("GREATER", "Greater", ""),
		("DIFF", "Different", ""),
		("EQUAL", "Equal", "")
		]

	comparisonTypeProperty = bpy.props.EnumProperty(name="Comparison", items=comparisonTypes, default="EQUAL", update=updateNode)
	

	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "A").number = 0.0
		self.inputs.new("mn_FloatSocket", "B").number = 1.0
		self.outputs.new("mn_BooleanSocket", "Result")
		allowCompiling()
		
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "comparisonTypeProperty")

	

	def execute(self, input):
		a = input["A"]
		b = input["B"]
		comp = self.comparisonTypeProperty
		output = {}
		
		if comp == "SMALLER_EQ":
			output["Result"] = a <= b

		elif comp == "SMALLER":
			output["Result"] = a < b

		elif comp == "GREATER_EQ":
			output["Result"] = a >= b

		elif comp == "GREATER":
			output["Result"] = a < b

		elif comp == "EQUAL":
			output["Result"] = a == b

		elif comp == "DIFF":
			output["Result"] = a != b

		return output

