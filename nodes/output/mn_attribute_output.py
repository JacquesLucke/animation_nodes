import bpy
from bpy.types import Node
from mn_node_helper import AnimationNode
from mn_execution import nodePropertyChanged

class AttributeOutputNode(Node, AnimationNode):
	bl_idname = "AttributeOutputNode"
	bl_label = "Attribute Output"
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("StringSocket", "Attribute")
		self.inputs.new("GenericSocket", "Value")
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		attribute = input["Attribute"]
		value = input["Value"]
		try:
			exec("object." + attribute + " = value")
		except:
			print("attribute not found or wrong data type - " + attribute)
		return {}
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)