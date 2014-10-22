import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodeTreeChanged, allowCompiling, forbidCompiling
import math

def updateNode(node, context):
	# singleInputOperations = ["SINE",
							 # "COSINE",
							 # "TANGENT",
							 # "ARCSINE",
							 # "ARCCOSINE",
							 # "ARCTANGENT",
							 # "ABSOLUTE"]
	# if node.mathTypesProperty in singleInputOperations and not node.inputs[-1].hide:
		# node.inputs[-1].hide = True
	# elif node.mathTypesProperty not in singleInputOperations and node.inputs[-1].hide:
		# node.inputs[-1].hide = False
	nodeTreeChanged()


class mn_VectorMathNode(Node, AnimationNode):
	bl_idname = "mn_VectorMathNode"
	bl_label = "Vector Math"
	
	mathTypes = [
		("ADD", "Add", ""),
		("SUBTRACT", "Subtract", "")]
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
		return ""
	def getModuleList(self):
		return ["math"]