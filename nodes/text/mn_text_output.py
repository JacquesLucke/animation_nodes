import bpy
from bpy.types import Node
from bpy.props import *
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

options = [ ("useText", "Text"),
			("useExtrude", "Extrude"),
			("useShear", "Shear"),
			("useSize", "Size"),
			("useLetterSpacing", "Letter Spacing"),
			("useWordSpacing", "Word Spacing"),
			("useLineSpacing", "Line Spacing"),
			("useXOffset", "X Offset"),
			("useYOffset", "Y Offset") ]

class mn_TextOutputNode(Node, AnimationNode):
	bl_idname = "mn_TextOutputNode"
	bl_label = "Text Output"
	
	def usePropertyChanged(self, context):
		self.setHideProperty()
		nodeTreeChanged()
	
	useText = BoolProperty(default = True, update = usePropertyChanged)
	useSize = BoolProperty(default = False, update = usePropertyChanged)
	useShear = BoolProperty(default = False, update = usePropertyChanged)
	useExtrude = BoolProperty(default = False, update = usePropertyChanged)
	
	useLetterSpacing = BoolProperty(default = False, update = usePropertyChanged)
	useWordSpacing = BoolProperty(default = False, update = usePropertyChanged)
	useLineSpacing = BoolProperty(default = False, update = usePropertyChanged)
	
	useXOffset = BoolProperty(default = False, update = usePropertyChanged)
	useYOffset = BoolProperty(default = False, update = usePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object")
		self.inputs.new("mn_StringSocket", "Text")
		self.inputs.new("mn_FloatSocket", "Extrude").number = 0.0
		self.inputs.new("mn_FloatSocket", "Shear").number = 0.0
		self.inputs.new("mn_FloatSocket", "Size").number = 1.0
		
		self.inputs.new("mn_FloatSocket", "Letter Spacing").number = 1.0
		self.inputs.new("mn_FloatSocket", "Word Spacing").number = 1.0
		self.inputs.new("mn_FloatSocket", "Line Spacing").number = 1.0
		
		self.inputs.new("mn_FloatSocket", "X Offset").number = 0.0
		self.inputs.new("mn_FloatSocket", "Y Offset").number = 0.0
		self.setHideProperty()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		col = layout.column(align = True)
		
		for i, option in enumerate(options[:3]):
			col.prop(self, option[0], text = option[1])
			
	def draw_buttons_ext(self, context, layout):
		col = layout.column(align = True)
		
		for i, option in enumerate(options):
			if i in [4, 7]: col.separator(); col.separator()
			col.prop(self, option[0], text = option[1])
		
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
		
	def setHideProperty(self):
		for option in options:
			self.inputs[option[1]].hide = not getattr(self, option[0])