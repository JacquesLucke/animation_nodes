import bpy
from bpy.types import Node
from mn_cache import getUniformRandom
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_interpolation_utils import *

topCategoryItems = [("LINEAR", "Linear", ""),
					("EXPONENTIAL", "Exponential", ""),
					("CUBIC", "Cubic", ""),
					("BACK", "Back", "")]
					
exponentialCategoryItems = [("IN", "In", ""),
							("OUT", "Out", "")]
							
cubicCategoryItems = [("IN", "In", ""),
					("OUT", "Out", ""),
					("INOUT", "In / Out", "")]
					
backCategoryItems = [("IN", "In", ""),
					("OUT", "Out", "")]

class mn_InterpolationNode(Node, AnimationNode):
	bl_idname = "mn_InterpolationNode"
	bl_label = "Interpolation"
	
	def topCategoryChanged(self, context):
		self.hideInputSockets()
		if self.topCategory == "BACK": self.inputs["Back"].hide = False
		nodePropertyChanged(self, context)
	
	topCategory = bpy.props.EnumProperty(items = topCategoryItems, default = "LINEAR", update = topCategoryChanged)
	backCategory = bpy.props.EnumProperty(items = backCategoryItems, default = "OUT", update = nodePropertyChanged)
	exponentialCategory = bpy.props.EnumProperty(items = exponentialCategoryItems, default = "OUT", update = nodePropertyChanged)
	cubicCategory = bpy.props.EnumProperty(items = cubicCategoryItems, default = "OUT", update = nodePropertyChanged)
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_FloatSocket", "Back").number = 1.70158
		self.outputs.new("mn_InterpolationSocket", "Interpolation")
		self.hideInputSockets()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "topCategory", text = "")
		if self.topCategory == "BACK": layout.prop(self, "backCategory", text = "")
		if self.topCategory == "EXPONENTIAL": layout.prop(self, "exponentialCategory", text = "")
		if self.topCategory == "CUBIC": layout.prop(self, "cubicCategory", text = "")
		
	def getInputSocketNames(self):
		return {"Back" : "back"}
	def getOutputSocketNames(self):
		return {"Interpolation" : "interpolation"}
		
	def execute(self, back):
		if self.topCategory == "LINEAR": return (linear, None)
		if self.topCategory == "EXPONENTIAL":
			if self.exponentialCategory == "IN": return (expoEaseIn, None)
			if self.exponentialCategory == "OUT": return (expoEaseOut, None)
		if self.topCategory == "CUBIC":
			if self.cubicCategory == "IN": return (cubicEaseIn, None)
			if self.cubicCategory == "OUT": return (cubicEaseOut, None)
			if self.cubicCategory == "INOUT": return (cubicEaseInOut, None)
		if self.topCategory == "BACK":
			if self.backCategory == "IN": return (backEaseIn, back)
			if self.backCategory == "OUT": return (backEaseOut, back)
		return (linear, None)
		
	def hideInputSockets(self):
		for socket in self.inputs:
			socket.hide = True
		