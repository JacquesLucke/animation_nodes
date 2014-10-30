import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_TextOutputNode(Node, AnimationNode):
	bl_idname = "mn_TextOutputNode"
	bl_label = "Text Output"
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object")
		self.inputs.new("mn_StringSocket", "Text")
		self.inputs.new("mn_FloatSocket", "Size").number = 1.0
		self.inputs.new("mn_FloatSocket", "Shear").number = 0.0
		self.inputs.new("mn_FloatSocket", "Extrude").number = 0.0
		
		self.inputs.new("mn_FloatSocket", "Letter Spacing").number = 1.0
		self.inputs.new("mn_FloatSocket", "Word Spacing").number = 1.0
		self.inputs.new("mn_FloatSocket", "Line Spacing").number = 1.0
		
		self.inputs.new("mn_FloatSocket", "X Offset").number = 0.0
		self.inputs.new("mn_FloatSocket", "Y Offset").number = 0.0
		allowCompiling()
		
	def execute(self, input):
		object = input["Object"]
		textObject = None
		
		if object is not None:
			textObject = bpy.data.curves.get(object.data.name)
		
		if textObject is not None:
			textObject.body = input["Text"]
			textObject.size = input["Size"]
			textObject.shear = input["Shear"]
			textObject.extrude = input["Extrude"]
			
			textObject.space_character = input["Letter Spacing"]
			textObject.space_word = input["Word Spacing"]
			textObject.space_line = input["Line Spacing"]
			
			textObject.offset_x = input["X Offset"]
			textObject.offset_y = input["Y Offset"]
		
		output = {}
		return output