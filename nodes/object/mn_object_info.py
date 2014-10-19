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
			
		output["Location"] = getArrayValueAtFrame(object, "location", frame)
		output["Rotation"] = getArrayValueAtFrame(object, "rotation_euler", frame)
		output["Scale"] = getArrayValueAtFrame(object, "scale", frame)
		
		beforeLoc = getArrayValueAtFrame(object, "location", frame - 1)
		beforeRot = getArrayValueAtFrame(object, "rotation_euler", frame - 1)
		beforeScale = getArrayValueAtFrame(object, "scale", frame - 1)
		
		for i in range(3):
			output["Location Velocity"][i] = output["Location"][i] - beforeLoc[i]
			
		for i in range(3):
			output["Rotation Velocity"][i] = output["Rotation"][i] - beforeRot[i]
			
		for i in range(3):
			output["Scale Velocity"][i] = output["Scale"][i] - beforeScale[i]
		
		return output