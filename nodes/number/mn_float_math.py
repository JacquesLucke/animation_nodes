import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
import math

def updateNode(node, context):
	singleInputOperations = ["SINE", "COSINE", "TANGENT", "ARCSINE", "ARCCOSINE", "ARCTANGENT", "ABSOLUTE", "FLOOR", "CEILING"]
	if node.mathTypesProperty in singleInputOperations and not node.inputs[-1].hide:
		node.inputs[-1].hide = True
	elif node.mathTypesProperty not in singleInputOperations and node.inputs[-1].hide:
		node.inputs[-1].hide = False
	nodeTreeChanged()


class mn_FloatMathNode(Node, AnimationNode):
	bl_idname = "mn_FloatMathNode"
	bl_label = "Math"
	isDetermined = True
	
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
		("ABSOLUTE", "Absolute", ""),
		("FLOOR", "Floor", ""),
		("CEILING", "Ceiling", "")]
	mathTypesProperty = bpy.props.EnumProperty(name="Operation", items=mathTypes, default="MULITPLY", update=updateNode)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "A")
		self.inputs.new("mn_FloatSocket", "B").number = 1.0
		self.outputs.new("mn_FloatSocket", "Result")
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"A" : "a", "B" : "b"}
	def getOutputSocketNames(self):
		return {"Result" : "result"}
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "mathTypesProperty")
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		if outputUse["Result"]:
			op = self.mathTypesProperty
			if op == "ADD": return "$result$ = %a% + %b%"
			elif op == "SUBTRACT": return "$result$ = %a% - %b%"
			elif op == "MULITPLY": return "$result$ = %a% * %b%"
			elif op == "DIVIDE": return '''
if %b% == 0: $result$ = 0
else: $result$ = %a% / %b%
'''
			elif op == "SINE": return "$result$ = math.sin(%a%)"
			elif op == "COSINE": return "$result$ = math.cos(%a%)"
			elif op == "TANGENT": return "$result$ = math.tan(%a%)"
			elif op == "ARCSINE": return "$result$ = math.asin(min(max(%a%, -1), 1))"
			elif op == "ARCCOSINE": return "$result$ = math.acos(min(max(%a%, -1), 1))"
			elif op == "ARCTANGENT": return "$result$ = math.atan(%a%)"
			elif op == "POWER": return "$result$ = math.pow(%a%, %b%)"
			elif op == "LOGARITHM": return '''
if %b% == 0: $result$ = math.log(%a%)
else: $result$ = math.log(%a%, %b%)
'''
			elif op == "MINIMUM": return "$result$ = min(%a%, %b%)"
			elif op == "MAXIMUM": return "$result$ = max(%a%, %b%)"
			elif op == "ROUND": return "$result$ = round(%a%, int(%b%))"
			elif op == "LESSTHAN": return "$result$ = %a% < %b%"
			elif op == "GREATHERTHAN": return "$result$ = %a% > %b%"
			elif op == "ABSOLUTE": return "$result$ = abs(%a%)"
			elif op == "MODULO": return '''
if %b% == 0: $result$ = 0
else: $result$ = %a% % %b%
'''
			elif op == "FLOOR": return "$result$ = math.floor(%a%)"
			elif op == "CEILING": return "$result$ = math.ceil(%a%)"
		return ""
	def getModuleList(self):
		return ["math"]