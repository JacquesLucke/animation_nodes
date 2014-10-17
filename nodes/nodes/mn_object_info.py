import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_object_utils import *
from bpy.props import BoolProperty

class mn_ObjectInfoNode(Node, AnimationNode):
	bl_idname = "mn_ObjectInfoNode"
	bl_label = "Object Info"
	
	frameTypes = [
		("OFFSET", "Offset", ""),
		("ABSOLUTE", "Absolute", "") ]
	frameTypesProperty = bpy.props.EnumProperty(name = "Frame Type", items = frameTypes, default = "OFFSET")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object")
		self.inputs.new("mn_FloatSocket", "Frame")
		self.outputs.new("mn_VectorSocket", "Location")
		self.outputs.new("mn_VectorSocket", "Rotation")
		self.outputs.new("mn_VectorSocket", "Scale")
		self.outputs.new("mn_VectorSocket", "Location Velocity")
		self.outputs.new("mn_VectorSocket", "Rotation Velocity")
		self.outputs.new("mn_VectorSocket", "Scale Velocity")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "frameTypesProperty")
		
	def execute(self, input):
		output = {}
		
		output["Location"] = [0, 0, 0]
		output["Rotation"] = [0, 0, 0]
		output["Scale"] = [1, 1, 1]
		output["Location Velocity"] = [0, 0, 0]
		output["Rotation Velocity"] = [0, 0, 0]
		output["Scale Velocity"] = [0, 0, 0]
		
		object = input["Object"]
		if object is None:
			return output
			
		if self.frameTypesProperty == "OFFSET":
			frame = getCurrentFrame()
			frame += input["Frame"]
		elif self.frameTypesProperty == "ABSOLUTE":
			frame = input["Frame"]
			
		output["Location"], output["Rotation"], output["Scale"] = getObjectTransformsAtFrame(object, frame)
		
		for i in range(3):
			output["Location Velocity"][i] = getFrameChange(object, frame, "location", i)
			
		for i in range(3):
			output["Rotation Velocity"][i] = getFrameChange(object, frame, "rotation_euler", i)
			
		for i in range(3):
			output["Scale Velocity"][i] = getFrameChange(object, frame, "scale", i)
		
		return output