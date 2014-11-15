import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class UpdateSettings(bpy.props.PropertyGroup):
	propertyChanged = bpy.props.BoolProperty(default = False, name = "Property Changed")
	frameChanged = bpy.props.BoolProperty(default = False, name = "Frame Changed")
	sceneUpdates = bpy.props.BoolProperty(default = False, name = "Scene Updates")

class mn_NetworkUpdateSettingsNode(Node, AnimationNode):
	bl_idname = "mn_NetworkUpdateSettingsNode"
	bl_label = "Update Settings"
	
	settings = bpy.props.PointerProperty(type = UpdateSettings, name = "Update Settings")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_NodeNetworkSocket", "Node Network").link_limit = 4095
		self.outputs.new("mn_NodeNetworkSocket", "Node Network").link_limit = 4095
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		layout.prop(self.settings, "propertyChanged")
		layout.prop(self.settings, "frameChanged")
		layout.prop(self.settings, "sceneUpdates")

	def execute(self, input):
		return {}
		
