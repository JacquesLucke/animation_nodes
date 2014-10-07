import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *
from bpy.props import BoolProperty

def updateNode(node, context):
		if "Frame" in node.inputs:
			node.inputs["Frame"].hide = node.useCurrentFrame
		nodePropertyChanged(node, context)

class ObjectInfoNode(Node, AnimationNode):
	bl_idname = "ObjectInfoNode"
	bl_label = "Object Info"
	
	useCurrentFrame = BoolProperty(default = True, update = updateNode)
	
	def init(self, context):
		self.inputs.new("ObjectSocket", "Object")
		self.inputs.new("FloatSocket", "Frame").hide = True
		self.outputs.new("VectorSocket", "Location")
		self.outputs.new("VectorSocket", "Rotation")
		self.outputs.new("VectorSocket", "Scale")
		self.outputs.new("VectorSocket", "Location Velocity")
		self.outputs.new("VectorSocket", "Rotation Velocity")
		self.outputs.new("VectorSocket", "Scale Velocity")
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "useCurrentFrame", text = "Use Current Frame")
		
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
			
		frame = input["Frame"]
		if self.useCurrentFrame: frame = getCurrentFrame()
			
		output["Location"], output["Rotation"], output["Scale"] = self.getTransforms(object, frame)
		
		for i in range(3):
			output["Location Velocity"][i] = self.getFrameChange(object, frame, "location", i)
			
		for i in range(3):
			output["Rotation Velocity"][i] = self.getFrameChange(object, frame, "rotation_euler", i)
			
		for i in range(3):
			output["Scale Velocity"][i] = self.getFrameChange(object, frame, "scale", i)
		
		return output
		
	def getTransforms(self, object, frame):
		location = [0, 0, 0]
		rotation = [0, 0, 0]
		scale = [1, 1, 1]
		
		for i in range(3):	
			location[i] = self.getValueAtFrame(object, "location", i, frame)
		for i in range(3):	
			rotation[i] = self.getValueAtFrame(object, "rotation_euler", i, frame)
		for i in range(3):	
			scale[i] = self.getValueAtFrame(object, "scale", i, frame)
		return location, rotation, scale
			
	def getValueAtFrame(self, object, dataPath, index, frame):
		fCurve = getFCurveWithDataPath(object, dataPath = dataPath, index = index)
		if fCurve is None:
			return eval("object." + dataPath + "[" + str(index) + "]")
		else:
			return fCurve.evaluate(frame)
		
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