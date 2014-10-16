import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ModifierOutputNode(Node, AnimationNode):
	bl_idname = "mn_ModifierOutputNode"
	bl_label = "Modifier Output"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("StringSocket", "Name").string = ""
		self.inputs.new("StringSocket", "Attribute").string = ""
		self.inputs.new("GenericSocket", "Value")
		allowCompiling()
		
	def execute(self, input):
		object = input["Object"]
		dataPath = 'modifiers["' + input["Name"] + '"].' + input["Attribute"]
		value = input["Value"]
		try:
			exec("object." + dataPath + " = value")
		except:
			pass
		return {}