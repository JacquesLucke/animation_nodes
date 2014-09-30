import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *

class ObjectInfoNode(Node, AnimationNode):
	bl_idname = "ObjectInfoNode"
	bl_label = "Object Info"
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.outputs.new("VectorSocket", "Location")
		self.outputs.new("VectorSocket", "Rotation")
		self.outputs.new("VectorSocket", "Scale")
		self.outputs.new("VectorSocket", "Location Velocity")
		self.outputs.new("VectorSocket", "Rotation Velocity")
		self.outputs.new("VectorSocket", "Scale Velocity")
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		output = {}
		
		output["Location"] = (0, 0, 0)
		output["Rotation"] = (0, 0, 0)
		output["Scale"] = (1, 1, 1)
		
		if object is None:
			return output
			
		output["Location"] = object.location
		output["Rotation"] = object.rotation_euler
		output["Scale"] = object.scale
		
		frame = getCurrentFrame()
		
		locationVelocity = [0, 0, 0]
		for i in range(3):
			locationVelocity[i] = self.getFrameChange(object, frame, "location", i)
			
		rotationVelocity = [0, 0, 0]
		for i in range(3):
			rotationVelocity[i] = self.getFrameChange(object, frame, "rotation_euler", i)
			
		scaleVelocity = [0, 0, 0]
		for i in range(3):
			scaleVelocity[i] = self.getFrameChange(object, frame, "scale", i)
			
		output["Location Velocity"] = locationVelocity
		output["Rotation Velocity"] = rotationVelocity
		output["Scale Velocity"] = scaleVelocity
		
		return output
		
	def getFrameChange(self, object, frame, dataPath, index):
		fCurve = getFCurveWithDataPath(object, dataPath = dataPath, index = index)
		if fCurve is None:
			return 0
		else:
			return fCurve.evaluate(frame) - fCurve.evaluate(frame - 1)
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)