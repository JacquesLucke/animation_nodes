import bpy
from bpy.types import Node
from mn_node_helper import AnimationNode
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
		self.outputs.new("FloatSocket", "X Velocity")
		
	def execute(self, input):
		object = bpy.data.objects.get(input["Object"])
		output = {}
		
		output["Location"] = (0, 0, 0)
		output["Rotation"] = (0, 0, 0)
		output["Scale"] = (1, 1, 1)
		
		frame = getCurrentFrame()
		fCurve = getFCurveWithDataPath(object, dataPath = "location", index = 0)
		if fCurve is None:
			output["X Velocity"] = 0
		else:
			output["X Velocity"] = fCurve.evaluate(frame) - fCurve.evaluate(frame - 1)
		
		if object is None:
			return output
			
		output["Location"] = object.location
		output["Rotation"] = object.rotation_euler
		output["Scale"] = object.scale
		
		return output
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)