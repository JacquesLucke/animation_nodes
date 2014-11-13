import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from mn_keyframes import *
from mn_math_utils import *

class mn_ObjectKeyframeInput(Node, AnimationNode):
	bl_idname = "mn_ObjectKeyframeInput"
	bl_label = "Object Keyframe Input"
	
	def keyframeChanged(self, context):
		self.buildOutputSockets()
		nodeTreeChanged()
	
	keyframe = bpy.props.EnumProperty(items = getKeyframeNameItems, name = "Keyframe", update = keyframeChanged)
	currentType = bpy.props.StringProperty(default = "Transforms")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_ObjectSocket", "Object").showName = False
		self.buildOutputSockets()
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "keyframe", text = "Keyframe")
		
	def buildOutputSockets(self):
		forbidCompiling()
		connections = getConnectionDictionaries(self)
		self.outputs.clear()
		type = getKeyframeType(self.keyframe)
		self.currentType == type
		if type == "Float":
			self.outputs.new("mn_FloatSocket", "Value")
		elif type == "Transforms":
			self.outputs.new("mn_VectorSocket", "Location")
			self.outputs.new("mn_VectorSocket", "Rotation")
			self.outputs.new("mn_VectorSocket", "Scale")
			self.outputs.new("mn_MatrixSocket", "Matrix")
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
		
	def execute(self, input):
		object = input["Object"]
		output = {}
		data = getKeyframe(object, self.keyframe, self.currentType)
		if self.currentType == "Float":
			output["Value"] = data
		elif self.currentType == "Transforms":
			output["Location"] = data[0]
			output["Rotation"] = data[1]
			output["Scale"] = data[2]
			output["Matrix"] = composeMatrix(data[0], data[1], data[2])
		return output