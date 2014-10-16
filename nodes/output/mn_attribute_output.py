import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_AttributeOutputNode(Node, AnimationNode):
	bl_idname = "mn_AttributeOutputNode"
	bl_label = "Attribute Output"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("StringSocket", "Attribute")
		self.inputs.new("GenericSocket", "Value")
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