import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_ObjectAttributeOutputNode(Node, AnimationNode):
	bl_idname = "mn_ObjectAttributeOutputNode"
	bl_label = "Object Attribute Output"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.inputs.new("mn_StringSocket", "Attribute").string = ""
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

classes = [
	mn_ObjectAttributeOutputNode
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
