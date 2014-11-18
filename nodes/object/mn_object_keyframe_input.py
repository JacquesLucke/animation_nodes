import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_keyframes import *
from animation_nodes.utils.mn_math_utils import *

currentTypes = {}

class mn_ObjectKeyframeInput(Node, AnimationNode):
	bl_idname = "mn_ObjectKeyframeInput"
	bl_label = "Object Keyframe Input"
	outputUseParameterName = "useOutput"
	
	def keyframeChanged(self, context):
		self.buildOutputSockets()
		nodeTreeChanged()
	
	keyframe = bpy.props.EnumProperty(items = getKeyframeNameItems, name = "Keyframe", update = keyframeChanged)
	
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
		currentTypes[getNodeIdentifier(self)] = type
		if type == "Float":
			self.outputs.new("mn_FloatSocket", "Value")
		elif type == "Transforms":
			self.outputs.new("mn_VectorSocket", "Location")
			self.outputs.new("mn_VectorSocket", "Rotation")
			self.outputs.new("mn_VectorSocket", "Scale")
			self.outputs.new("mn_MatrixSocket", "Matrix")
		elif type == "Vector":
			self.outputs.new("mn_VectorSocket", "Vector")
		tryToSetConnectionDictionaries(self, connections)
		allowCompiling()
		
	def getInputSocketNames(self):
		return {"Object" : "object"}
	def getOutputSocketNames(self):
		type = getKeyframeType(self.keyframe)
		currentTypes[getNodeIdentifier(self)] = type	
		if type == "Float":
			return {"Value" : "value"}
		elif type == "Transforms":
			return {"Location" : "location",
					"Rotation" : "rotation",
					"Scale" : "scale",
					"Matrix" : "matrix"}
		elif type == "Vector":
			return {"Vector" : "vector"}
		
	def execute(self, useOutput, object):
		type = currentTypes[getNodeIdentifier(self)]
		data = getKeyframe(object, self.keyframe, type)
		if type in ["Float", "Vector"]:	return data
		elif type == "Transforms":
			if useOutput["Matrix"]:
				return data[0], data[1], data[2], composeMatrix(data[0], data[1], data[2])
			else:
				return data[0], data[1], data[2], None

classes = [
	mn_ObjectKeyframeInput
]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
