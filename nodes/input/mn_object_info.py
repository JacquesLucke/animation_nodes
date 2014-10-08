import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged
from mn_utils import *
from mn_object_utils import *
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
			
		output["Location"], output["Rotation"], output["Scale"] = getObjectTransformsAtFrame(object, frame)
		
		for i in range(3):
			output["Location Velocity"][i] = getFrameChange(object, frame, "location", i)
			
		for i in range(3):
			output["Rotation Velocity"][i] = getFrameChange(object, frame, "rotation_euler", i)
			
		for i in range(3):
			output["Scale Velocity"][i] = getFrameChange(object, frame, "scale", i)
		
		return output
		
		
# register
################################
		
def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)