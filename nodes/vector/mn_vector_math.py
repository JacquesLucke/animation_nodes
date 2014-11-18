import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
import math

def updateNode(node, context):
	nodeTreeChanged()


class mn_VectorMathNode(Node, AnimationNode):
	bl_idname = "mn_VectorMathNode"
	bl_label = "Vector Math"
	isDetermined = True
	
	mathTypes = [
		("ADD", "Add", ""),
		("SUBTRACT", "Subtract", ""),
		("MULTIPLY", "Multiply", "Multiply element by element"),
		("DIVIDE", "Divide", ""),
        ("CROSS", "Cross Product", "Calculate the cross/vector product, yielding a vector that is orthogonal to both input vectors")]
	mathTypesProperty = bpy.props.EnumProperty(name="Operation", items=mathTypes, default="ADD", update=updateNode)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_VectorSocket", "A")
		self.inputs.new("mn_VectorSocket", "B")
		self.outputs.new("mn_VectorSocket", "Result")
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
			if op == "ADD": return "$result$ = [%a%[0] + %b%[0], %a%[1] + %b%[1], %a%[2] + %b%[2]]"
			elif op == "SUBTRACT": return "$result$ = [%a%[0] - %b%[0], %a%[1] - %b%[1], %a%[2] - %b%[2]]"
			elif op == "MULTIPLY": return "$result$ = [%a%[0] * %b%[0], %a%[1] * %b%[1], %a%[2] * %b%[2]]"
			elif op == "DIVIDE": return '''
$result$ = [0, 0, 0]
if %b%[0] != 0: $result$[0] = %a%[0] / %b%[0]
if %b%[1] != 0: $result$[1] = %a%[1] / %b%[1]
if %b%[2] != 0: $result$[2] = %a%[2] / %b%[2]
'''
			elif op == "CROSS": return "$result$ = [%a%[1] * %b%[2] - %a%[2] * %b%[1], %a%[2] * %b%[0] - %a%[0] * %b%[2], %a%[0] * %b%[1] - %a%[1] * %b%[0]]"
		return ""
	def getModuleList(self):
		return ["math"]


classes = [
	mn_VectorMathNode
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
