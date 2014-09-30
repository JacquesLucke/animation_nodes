import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged

class FloatMathNode(Node, AnimationNode):
	bl_idname = "FloatMathNode"
	bl_label = "Math (Float)"
	
	mathTypes = [
		("ADD", "Add", ""),
		("SUBTRACT", "Subtract", ""),
		("MULITPLY", "Multiply", ""),
		("DIVIDE", "Divide", ""),
		("MODULO", "Modulo", "")]
	mathTypesProperty = bpy.props.EnumProperty(name = "Type", items = mathTypes, default = "ADD", update = nodePropertyChanged)
	
	def init(self, context):
		self.inputs.new("FloatSocket", "A")
		self.inputs.new("FloatSocket", "B")
		self.outputs.new("FloatSocket", "Result")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "mathTypesProperty")
		
	def execute(self, input):
		a = input["A"]
		b = input["B"]
		result = 0
		type = self.mathTypesProperty
		try:
			if type == "ADD": result = a + b
			elif type == "SUBTRACT": result = a - b
			elif type == "MULITPLY": result = a * b
			elif type == "DIVIDE": result = a / b
			elif type == "MODULO": result = a % b
		except (ZeroDivisionError):
			print("ZeroDivisionError - " + self.name)
		output = {}
		output["Result"] = result
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)