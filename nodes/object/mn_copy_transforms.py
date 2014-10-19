import bpy, time
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_object_utils import *
from mn_utils import *
from mn_cache import *

class mn_CopyTransformsNode(Node, AnimationNode):
	bl_idname = "mn_CopyTransformsNode"
	bl_label = "Copy Transforms"
	
	useLocation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	useRotation = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	useScale = bpy.props.BoolVectorProperty(update = nodePropertyChanged)
	
	frameTypes = [
		("OFFSET", "Offset", ""),
		("ABSOLUTE", "Absolute", "") ]
	frameTypesProperty = bpy.props.EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET")
	
	def init(self, context):
		forbidCompiling()
		fromSocket = self.inputs.new("mn_ObjectSocket", "From")
		fromSocket.showName = True
		toSocket = self.inputs.new("mn_ObjectSocket", "To")
		toSocket.showName = True
		self.inputs.new("mn_FloatSocket", "Frame")
		self.outputs.new("mn_ObjectSocket", "To")
		self.width = 200
		allowCompiling()
		
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
		
	def getInputSocketNames(self):
		return {"From" : "fromObject",
				"To" : "toObject",
				"Frame" : "frame"}
	def getOutputSocketNames(self):
		return {"To" : "toObject"}
		
	def execute(self, fromObject, toObject, frame):
		if fromObject is None or toObject is None:
			return toObject
			
		if self.frameTypesProperty == "OFFSET":
			frame += getCurrentFrame()
	
		useLoc = self.useLocation
		useRot = self.useRotation
		useScale = self.useScale
		
		if useLoc[0] and useLoc[1] and useLoc[2]:
			toObject.location = getArrayValueAtFrame(fromObject, "location", frame)
		else:
			for i in range(3):
				if useLoc[i]:
					toObject.location[i] = getSingleValueOfArrayAtFrame(fromObject, "location", index = i, frame = frame)
					
		if useRot[0] and useRot[1] and useRot[2]:
			toObject.rotation_euler = getArrayValueAtFrame(fromObject, "rotation_euler", frame)
		else:
			for i in range(3):
				if useRot[i]:
					toObject.rotation_euler[i] = getSingleValueOfArrayAtFrame(fromObject, "rotation_euler", index = i, frame = frame)
					
		if useScale[0] and useScale[1] and useScale[2]:
			toObject.scale = getArrayValueAtFrame(fromObject, "scale", frame)
		else:
			for i in range(3):
				if useScale[i]:
					toObject.scale[i] = getSingleValueOfArrayAtFrame(fromObject, "scale", index = i, frame = frame)
					
		return toObject