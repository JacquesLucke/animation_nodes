import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from mn_utils import *
from mn_object_utils import *
from bpy.props import BoolProperty
from operator import sub

class mn_ObjectInfoNode(Node, AnimationNode):
	bl_idname = "mn_ObjectInfoNode"
	bl_label = "Object Info"
	outputUseParameterName = "useOutput"
	
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
		
	def getInputSocketNames(self):
		return {"Object" : "object",
				"Frame" : "frame"}
	def getOutputSocketNames(self):
		return {"Location" : "location",
				"Rotation" : "rotation",
				"Scale" : "scale",
				"Location Velocity" : "locVelocity",
				"Rotation Velocity" : "rotVelocity",
				"Scale Velocity" : "scaleVelocity"}
		
	def execute(self, useOutput, object, frame):
		location = [0, 0, 0]
		rotation = [0, 0, 0]
		scale = [1, 1, 1]
		locVelocity = [0, 0, 0]
		rotVelocity = [0, 0, 0]
		scaleVelocity = [0, 0, 0]
		
		if object is None:
			return location, rotation, scale, locVelocity, rotVelocity, scaleVelocity
		if self.frameTypesProperty == "OFFSET":
			frame += getCurrentFrame()
			
		if useOutput["Location Velocity"]:
			[locationBefore, location] = getArrayValueAtMultipleFrames(object, "location", [frame-1, frame])
			locVelocity = list(map(sub, location, locationBefore))
		elif useOutput["Location"]:
			location = getArrayValueAtFrame(object, "location", frame)
			
		if useOutput["Rotation Velocity"]:
			[rotationBefore, rotation] = getArrayValueAtMultipleFrames(object, "rotation_euler", [frame-1, frame])
			rotVelocity = list(map(sub, rotation, rotationBefore))
		elif useOutput["Rotation"]:
			rotation = getArrayValueAtFrame(object, "rotation_euler", frame)
			
		if useOutput["Scale Velocity"]:
			[scaleBefore, scale] = getArrayValueAtMultipleFrames(object, "scale", [frame-1, frame])
			scaleVelocity = list(map(sub, scale, scaleBefore))
		elif useOutput["Scale"]:
			scale = getArrayValueAtFrame(object, "scale", frame)
		
		return location, rotation, scale, locVelocity, rotVelocity, scaleVelocity