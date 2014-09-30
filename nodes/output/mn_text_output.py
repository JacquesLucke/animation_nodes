import bpy
from bpy.types import Node
from mn_node_helper import AnimationNode
from mn_execution import nodePropertyChanged

class TextOutputNode(Node, AnimationNode):
	bl_idname = "TextOutputNode"
	bl_label = "Text Output"
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("StringSocket", "Text")
		self.inputs.new("FloatSocket", "Size").number = 1.0
		self.inputs.new("FloatSocket", "Shear").number = 0.0
		self.inputs.new("FloatSocket", "Extrude").number = 0.1
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		textObject = None
		
		if object is not None:
			textObject = bpy.data.curves.get(object.data.name)
		
		if textObject is not None:
			textObject.body = input["Text"]
			textObject.size = input["Size"]
			textObject.shear = input["Shear"]
			textObject.extrude = input["Extrude"]
		
		output = {}
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)