import bpy
from bpy.types import Node
from mn_node_base import AnimationNode
from mn_utils import *
from mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class UpdateSettings(bpy.types.PropertyGroup):
	propertyChanged = bpy.props.BoolProperty(default = False, name = "Property Changed")
	frameChanged = bpy.props.BoolProperty(default = False, name = "Frame Changed")
	sceneUpdates = bpy.props.BoolProperty(default = False, name = "Scene Updates")
	treeChanged = bpy.props.BoolProperty(default = False, name = "Tree Changed")
	forceExecution = bpy.props.BoolProperty(default = False, name = "Force Execution")

class mn_NetworkUpdateSettingsNode(Node, AnimationNode):
	bl_idname = "mn_NetworkUpdateSettingsNode"
	bl_label = "Update Settings"
	
	settings = bpy.props.PointerProperty(type = UpdateSettings, name = "Update Settings")
	
	def init(self, context):
		forbidCompiling()
		self.inputs.new("mn_NodeNetworkSocket", "Node Network").link_limit = 4095
		allowCompiling()
		
	def draw_buttons(self, context, layout):
		forceUpdate = layout.operator("mn.force_local_node_tree_execution", "Force Update")
		forceUpdate.nodeTreeName = self.id_data.name
		forceUpdate.nodeName = self.name
		layout.prop(self.settings, "propertyChanged")
		layout.prop(self.settings, "frameChanged")
		layout.prop(self.settings, "sceneUpdates")
		layout.prop(self.settings, "treeChanged")

	def execute(self, input):
		return {}
		
		
class ForceLocalNodeTreeExecution(bpy.types.Operator):
	bl_idname = "mn.force_local_node_tree_execution"
	bl_label = "Force Local Node Tree Execution"
	
	nodeTreeName = bpy.props.StringProperty()
	nodeName = bpy.props.StringProperty()
		
	def execute(self, context):
		node = getNode(self.nodeTreeName, self.nodeName)
		node.settings.forceExecution = True
		return {'FINISHED'}