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
	useExtrude = BoolProperty(default = False, update = usePropertyChanged)
	useShear = BoolProperty(default = False, update = usePropertyChanged)
	useSize = BoolProperty(default = False, update = usePropertyChanged)
	
	useLetterSpacing = BoolProperty(default = False, update = usePropertyChanged)
	useWordSpacing = BoolProperty(default = False, update = usePropertyChanged)
	useLineSpacing = BoolProperty(default = False, update = usePropertyChanged)
	
	useXOffset = BoolProperty(default = False, update = usePropertyChanged)
	useYOffset = BoolProperty(default = False, update = usePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		
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
		
	def setHideProperty(self):
		for option in options:
			self.inputs[option[1]].hide = not getattr(self, option[0])
			
			
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Text" : "text",
				"Size" : "size",
				"Shear" : "shear",
				"Extrude" : "extrude",
				"Letter Spacing" : "letterSpacing",
				"Word Spacing" : "wordSpacing",
				"Line Spacing" : "lineSpacing",
				"X Offset" : "xOffset",
				"Y Offset" : "yOffset"}
	def getOutputSocketNames(self):
		return {}
		
	def useInLineExecution(self):
		return True
	def getInLineExecutionString(self, outputUse):
		codeLines = []
		codeLines.append("if %object% is not None:")
		codeLines.append("    textObject = None")
		codeLines.append("    if %object%.type == 'FONT': textObject = %object%.data")
		codeLines.append("    if textObject is not None:")
		
		if self.useText: codeLines.append(" "*8 + "textObject.body = %text%")
		if self.useExtrude: codeLines.append(" "*8 + "textObject.extrude = %extrude%")
		if self.useShear: codeLines.append(" "*8 + "textObject.shear = %shear%")
		if self.useSize: codeLines.append(" "*8 + "textObject.size = %size%")
		
		if self.useLetterSpacing: codeLines.append(" "*8 + "textObject.space_character = %letterSpacing%")
		if self.useWordSpacing: codeLines.append(" "*8 + "textObject.space_word = %wordSpacing%")
		if self.useLineSpacing: codeLines.append(" "*8 + "textObject.space_line = %lineSpacing%")
		
		if self.useXOffset: codeLines.append(" "*8 + "textObject.offset_x = %xOffset%")
		if self.useYOffset: codeLines.append(" "*8 + "textObject.offset_y = %yOffset%")
		
		codeLines.append(" "*8 + "pass")
		
		return "\n".join(codeLines)