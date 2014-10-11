import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
import math

def updateNode(node, context):
	nodePropertyChanged(node, context)
	singleInputOperations = ["SINE",
							 "COSINE",
							 "TANGENT",
							 "ARCSINE",
							 "ARCCOSINE",
							 "ARCTANGENT",
							 "ABSOLUTE"]
	if node.mathTypesProperty in singleInputOperations and not node.inputs[-1].hide:
		node.inputs[-1].hide = True
	elif node.mathTypesProperty not in singleInputOperations and node.inputs[-1].hide:
		node.inputs[-1].hide = False


class FloatMathNode(Node, AnimationNode):
	bl_idname = "FloatMathNode"
	bl_label = "Math (Float)"
	
	mathTypes = [
		("ADD", "Add", ""),
		("SUBTRACT", "Subtract", ""),
		("MULITPLY", "Multiply", ""),
		("DIVIDE", "Divide", ""),
		("SINE", "Sine", ""),
		("COSINE", "Cosine", ""),
		("TANGENT", "Tangent", ""),
		("ARCSINE", "Arcsine", ""),
		("ARCCOSINE", "Arccosine", ""),
		("ARCTANGENT", "Arctangent", ""),
		("POWER", "Power", ""),
		("LOGARITHM", "Logarithm", ""),
		("MINIMUM", "Minimum", ""),
		("MAXIMUM", "Maximum", ""),
		("ROUND", "Round", ""),
		("LESSTHAN", "Less Than", ""),
		("GREATHERTHAN", "Greather Than", ""),
		("MODULO", "Modulo", ""),
		("ABSOLUTE", "Absolute", "")]
	mathTypesProperty = bpy.props.EnumProperty(name="Operation", items=mathTypes, default="ADD", update=updateNode)
	
	def init(self, context):
		self.inputs.new("FloatSocket", "A")
		self.inputs.new("FloatSocket", "B")
		self.outputs.new("FloatSocket", "Result")
		
	def getSocketVariableConnections(self):
		return ({"A" : "a", "B" : "b"}, {"Result" : "result"})
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "mathTypesProperty")
		
	def execute(self, a, b):
		result = 0
		operation = self.mathTypesProperty
		try:
			if operation == "ADD": result = a + b
			elif operation == "SUBTRACT": result = a - b
			elif operation == "MULITPLY": result = a * b
			elif operation == "DIVIDE": result = a / b
			elif operation == "SINE": result = math.sin(a)
			elif operation == "COSINE": result = math.cos(a)
			elif operation == "TANGENT": result = math.tan(a)
			elif operation == "ARCSINE":
				if a > 1:
					a = 1
					print("Clamping A to 1")
				elif a < -1:
					a = -1
					print("Clamping A to -1")
				result = math.asin(a)
			elif operation == "ARCCOSINE":
				if a > 1:
					a = 1
					print("Clamping A to 1")
				elif a < -1:
					a = -1
					print("Clamping A to -1")
				result = math.acos(a)
			elif operation == "ARCTANGENT": result = math.atan(a)
			elif operation == "POWER": result = math.pow(a, b)
			elif operation == "LOGARITHM":
				if b == 0:
					result = math.log(a)
				else:
					result = math.log(a, b)
			elif operation == "MINIMUM": result = min(a, b)
			elif operation == "MAXIMUM": result = max(a, b)
			elif operation == "ROUND": result = round(a, int(b))
			elif operation == "LESSTHAN":
				if b < a:
					result = True
				else:
					result = False
			elif operation == "GREATHERTHAN":
				if b > a:
					result = True
				else:
					result = False
			elif operation == "MODULO": result = a % b
			elif operation == "ABSOLUTE": result = abs(a)
		except ZeroDivisionError as e:
			print("ZeroDivisionError: {error} - {name}".format(error=e, name=self.name))
		except ValueError as e:
			print("ValueError: {error} - {name}".format(error=e, name=self.name))
		return result
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)