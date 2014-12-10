import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from animation_nodes.mn_utils import *

keyframePathItems = (
	("location", "Location", ""),
	("rotation_euler", "Rotation", ""),
	("scale", "Scale", ""))

class mn_BakeToKeyframes(Node, AnimationNode):
	bl_idname = "mn_BakeToKeyframes"
	bl_label = "Bake to Keyframes"
	
	selectedPathType = bpy.props.EnumProperty(default = "location", items = keyframePathItems, name = "Path Type")
	attributePath = bpy.props.StringProperty(default = "", name = "Attribute Path")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_BooleanSocket", "Enable")
		self.inputs.new("mn_BooleanSocket", "Set Keyframe")
		self.inputs.new("mn_BooleanSocket", "Remove Unwanted")
		self.inputs.new("mn_ObjectSocket", "Object")
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self, "selectedPathType")
		
	def getInputSocketNames(self):
		return {"Enable" : "enable",
				"Set Keyframe" : "setKeyframe",
				"Remove Unwanted" : "removeUnwanted",
				"Object" : "object"}
	def getOutputSocketNames(self):
		return {}
		
	def execute(self, enable, setKeyframe, removeUnwanted, object):
		if not enable: return
		if setKeyframe:
			try: object.keyframe_insert(data_path = self.selectedPathType, frame = getCurrentFrame())
			except: pass
		elif removeUnwanted:
			try: object.keyframe_delete(data_path = self.selectedPathType, frame = getCurrentFrame())
			except: pass
		
		

