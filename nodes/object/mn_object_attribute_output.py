import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

class mn_ObjectAttributeOutputNode(Node, AnimationNode):
	bl_idname = "mn_ObjectAttributeOutputNode"
	bl_label = "Object Attribute Output"
	
	attribute = bpy.props.StringProperty(default = "", name = "Attribute", update = nodeTreeChanged)
	
	def init(self, context):
		forbidCompiling()
		self.width = 200
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_GenericSocket", "Value")
		self.outputs.new("mn_ObjectSocket", "Object")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "attribute")
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Value" : "value"}
	def getOutputSocketNames(self):
		return {"Object" : "object"}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = [
			"try:",
			"    %object%." + self.attribute + " = %value%",
			"except: pass",
			"$object$ = %object%" ]
		if isValidCode(self.attribute) and self.attribute != "":
			return "\n".join(codeLines)
		return "$object$ = %object%"

