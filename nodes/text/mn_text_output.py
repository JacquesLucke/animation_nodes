import bpy
from bpy.types import Node
from bpy.props import *
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

options = [ ("useText", "Text", "Text"),
			("useSize", "Size", "Size"),
			("useShear", "Shear", "Shear"),
			("useExtrude", "Extrude", "Extrude"),
			("useLetterSpacing", "Letter Spacing", "Letter Spacing"),
			("useWordSpacing", "Word Spacing", "Word Spacing"),
			("useLineSpacing", "Line Spacing", "Line Spacing"),
			("useXOffset", "X Offset", "X Offset"),
			("useYOffset", "Y Offset", "Y Offset") ]

class mn_TextOutputNode(Node, AnimationNode):
	bl_idname = "mn_TextOutputNode"
	bl_label = "Text Output"
	
	useText = BoolProperty(default = False, update = nodeTreeChanged)
	useSize = BoolProperty(default = False, update = nodeTreeChanged)
	useShear = BoolProperty(default = False, update = nodeTreeChanged)
	useExtrude = BoolProperty(default = False, update = nodeTreeChanged)
	
	useLetterSpacing = BoolProperty(default = False, update = nodeTreeChanged)
	useWordSpacing = BoolProperty(default = False, update = nodeTreeChanged)
	useLineSpacing = BoolProperty(default = False, update = nodeTreeChanged)
	
	useXOffset = BoolProperty(default = False, update = nodeTreeChanged)
	useYOffset = BoolProperty(default = False, update = nodeTreeChanged)
	
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
		
	def draw_buttons(self, context, layout):
		col = layout.column(align = True)
		
		for i, option in enumerate(options):
			if i in [4, 7]: col.separator(); col.separator()
			row = col.row(align = True)
			row.prop(self, option[0], text = option[1])
			row.prop(self.inputs[option[2]], "hide")
		
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