import bpy, time
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged
from mn_object_utils import *
from mn_utils import *
from mn_cache import *

class CopyTransformsNode(Node, AnimationNode):
	bl_idname = "CopyTransformsNode"
	bl_label = "Copy Transforms"
	
	useLocation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	useRotation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	useScale = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	
	frameTypes = [
		("OFFSET", "Offset", ""),
		("ABSOLUTE", "Absolute", "") ]
	frameTypesProperty = bpy.props.EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET")
	
	def init(self, context):
		fromSocket = self.inputs.new("ObjectSocket", "From")
		fromSocket.showName = True
		toSocket = self.inputs.new("ObjectSocket", "To")
		toSocket.showName = True
		self.inputs.new("FloatSocket", "Frame")
		self.outputs.new("ObjectSocket", "To")
		self.width = 200
		
	def draw_buttons(self, context, layout):
		col = layout.column(align = True)
		
		row = col.row(align = True)
		row.label("Location")
		row.prop(self, "useLocation", index = 0, text = "X")
		row.prop(self, "useLocation", index = 1, text = "Y")
		row.prop(self, "useLocation", index = 2, text = "Z")
		row = col.row(align = True)
		row.label("Rotation")
		row.prop(self, "useRotation", index = 0, text = "X")
		row.prop(self, "useRotation", index = 1, text = "Y")
		row.prop(self, "useRotation", index = 2, text = "Z")
		row = col.row(align = True)
		row.label("Scale")
		row.prop(self, "useScale", index = 0, text = "X")
		row.prop(self, "useScale", index = 1, text = "Y")
		row.prop(self, "useScale", index = 2, text = "Z")
		
		layout.prop(self, "frameTypesProperty")
		
	def execute(self, input):
		fromObject = input["From"]
		toObject = input["To"]
		if fromObject is None or toObject is None:
			return { "To" : None }
			
		if self.frameTypesProperty == "OFFSET":
			frame = getCurrentFrame()
			frame += input["Frame"]
		elif self.frameTypesProperty == "ABSOLUTE":
			frame = input["Frame"]
		
		fCurves = self.getFCurvesFromCache(fromObject)
		for i in range(3):
			if self.useLocation[i]:
				if fCurves["loc"][i] is None: toObject.location[i] = fromObject.location[i]
				else: toObject.location[i] = fCurves["loc"][i].evaluate(frame)
		for i in range(3):
			if self.useRotation[i]:
				if fCurves["rot"][i] is None: toObject.rotation_euler[i] = fromObject.rotation_euler[i]
				else: toObject.rotation_euler[i] = fCurves["rot"][i].evaluate(frame)
		for i in range(3):
			if self.useScale[i]:
				if fCurves["scale"][i] is None: toObject.scale[i] = fromObject.scale[i]
				else: toObject.scale[i] = fCurves["scale"][i].evaluate(frame)
		return { "To" : toObject}
		
	def getFCurvesFromCache(self, fromObject):
		context = fromObject.name
		cache = getExecutionCache(self)
		if cache is None:
			cache = {}
		if context not in cache:
			fCurves = {}
			
			fCurves["loc"] = [None, None, None]
			fCurves["rot"] = [None, None, None]
			fCurves["scale"] = [None, None, None]
			
			for i in range(3):
				fCurves["loc"][i] = getFCurveWithDataPath(fromObject, "location", index = i)
			for i in range(3):
				fCurves["rot"][i] = getFCurveWithDataPath(fromObject, "rotation_euler", index = i)
			for i in range(3):
				fCurves["scale"][i] = getFCurveWithDataPath(fromObject, "scale", index = i)
			
			cache[context] = fCurves
			setExecutionCache(self, cache)
		return cache[context]
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)