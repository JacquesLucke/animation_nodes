import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ObjectAttributeOutputNode(Node, AnimationNode):
	bl_idname = "mn_ObjectAttributeOutputNode"
	bl_label = "Object Attribute Output"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_StringSocket", "Attribute")
		self.inputs.new("mn_GenericSocket", "Value")
		allowCompiling()
		
	def execute(self, input):
		object = input["Object"]
		attribute = input["Attribute"]
		value = input["Value"]
		try:
			exec("object." + attribute + " = value")
		except:
			pass
		return {}