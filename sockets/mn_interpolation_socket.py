import bpy
from bpy.types import NodeTree, Node, NodeSocket
from mn_utils import *
from mn_execution import nodePropertyChanged
from mn_interpolation_utils import *

class InterpolationCategory:
	def __init__(self, identifier, name):
		self.identifier = identifier
		self.name = name
		self.interpolationModes = []
	def append(self, mode):
		self.interpolationModes.append(mode)
		
class InterpolationMode:
	def __init__(self, identifier, name):
		self.identifier = identifier
		self.name = name

interpolationEnum = []
linearMode = InterpolationMode("LINEAR", "Linear")

easingCategory = InterpolationCategory("EASING", "Easing")
easingCategory.append(InterpolationMode("IN", "Ease In"))
easingCategory.append(InterpolationMode("OUT", "Ease Out"))
easingCategory.append(InterpolationMode("INOUT", "Ease In Out"))

backCategory = InterpolationCategory("BACK", "Back")
backCategory.append(InterpolationMode("IN", "In"))
backCategory.append(InterpolationMode("OUT", "Out"))

interpolationEnum.append(linearMode)
interpolationEnum.append(easingCategory)
interpolationEnum.append(backCategory)

def getInterpolationFunctionTupel(mode, subMode):
	if mode == "LINEAR": return (linear, None)
	if mode == "EASING":
		if subMode == "IN": return (cubicEaseIn, None)
		if subMode == "OUT": return (cubicEaseOut, None)
		if subMode == "INOUT": return (cubicEaseInOut, None)
	if mode == "BACK":
		if subMode == "IN": return (backEaseIn, 1.70158)
		if subMode == "OUT": return (backEaseOut, 1.70158)
	return (linear, None)


class mn_InterpolationSocket(NodeSocket):
	bl_idname = "mn_InterpolationSocket"
	bl_label = "Interpolation Socket"
	dataType = "Interpolation"
	allowedInputTypes = ["Interpolation"]
	
	def getCategoryEnumItems(self, context):
		items = []
		for interpolation in interpolationEnum:
			items.append((interpolation.identifier, interpolation.name, ""))
		if len(items) == 0: items.append(("None", "None", ""))
		return items
	def getSubModeItems(self, context):
		items = []
		mode = self.getCurrentMode()
		if type(mode) == InterpolationCategory:
			for interpolation in mode.interpolationModes:
				items.append((interpolation.identifier, interpolation.name, ""))
		if len(items) == 0: items.append(("None", "None", ""))
		return items
	
	mode = bpy.props.EnumProperty(name = "Mode", items = getCategoryEnumItems, update = nodePropertyChanged)
	subMode = bpy.props.EnumProperty(name = "SubMode", items = getSubModeItems, update = nodePropertyChanged)
	
	def draw(self, context, layout, node, text):
		if not self.is_output and not isSocketLinked(self):
			col = layout.column(align = False)
			col.label(text)
			row = col.row(align = True)
			row.prop(self, "mode", text = "")
			mode = self.getCurrentMode()
			if type(mode) == InterpolationCategory:
				row.prop(self, "subMode", text = "")
		else:
			layout.label(text)
			
	def draw_color(self, context, node):
		return (0.3, 0.8, 0.3, 1)
		
	def getValue(self):
		return getInterpolationFunctionTupel(self.mode, self.subMode)
		
	def setStoreableValue(self, data):
		self.mode = data
	def getStoreableValue(self):
		return self.mode
		
	def getCurrentMode(self):
		for mode in interpolationEnum:
			if mode.identifier == self.mode:
				return mode
		return None
				
		
# register
################################
	
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)