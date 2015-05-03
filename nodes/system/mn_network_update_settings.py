import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_utils import *
from animation_nodes.mn_execution import nodePropertyChanged, forceExecution, allowCompiling, forbidCompiling

class UpdateSettings(bpy.types.PropertyGroup):
    propertyChanged = bpy.props.BoolProperty(default = False, name = "Property Changed")
    frameChanged = bpy.props.BoolProperty(default = False, name = "Frame Changed")
    sceneUpdates = bpy.props.BoolProperty(default = False, name = "Scene Updates")
    treeChanged = bpy.props.BoolProperty(default = False, name = "Tree Changed")
    skipFramesAmount = bpy.props.IntProperty(default = 0, name = "Skip Frames", min = 0, soft_max = 10)
    unitName = bpy.props.StringProperty(default = "Unit", name = "Unit Name")
    printTime = bpy.props.BoolProperty(default = False, name = "Print Update Time")
    
class mn_NetworkUpdateSettingsNode(Node, AnimationNode):
    bl_idname = "mn_NetworkUpdateSettingsNode"
    bl_label = "Update Settings"
    needsExecution = False
    
    def useAsExecuteButtonChanged(self, context):
        if self.useAsExecuteButton:
            self.settings.propertyChanged = False
            self.settings.frameChanged = False
            self.settings.sceneUpdates = False
            self.settings.treeChanged = False
            
    
    settings = bpy.props.PointerProperty(type = UpdateSettings, name = "Update Settings")
    executionTime = bpy.props.FloatProperty(name = "Execution Time")
    
    useAsExecuteButton = bpy.props.BoolProperty(name = "Use as Execute Button", default = False, update = useAsExecuteButtonChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_NodeNetworkSocket", "Node Network").link_limit = 4095
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        if self.useAsExecuteButton:
            row = layout.row()
            row.scale_y = 1.5
            forceUpdate = row.operator("mn.force_local_node_tree_execution", "Execute")
            forceUpdate.nodeTreeName = self.id_data.name
            forceUpdate.nodeName = self.name
        else:
            forceUpdate = layout.operator("mn.force_local_node_tree_execution", "Force Update")
            forceUpdate.nodeTreeName = self.id_data.name
            forceUpdate.nodeName = self.name
            layout.prop(self.settings, "treeChanged")
            layout.prop(self.settings, "propertyChanged")
            layout.prop(self.settings, "sceneUpdates")
            layout.prop(self.settings, "frameChanged")
            if self.settings.frameChanged:
                layout.prop(self.settings, "skipFramesAmount", slider = True)
            layout.separator()
            layout.prop(self.settings, "printTime")
            layout.prop(self.settings, "unitName")
            layout.separator()
        layout.label("Time: " + str(round(self.executionTime, 6)) + " s")
            
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "useAsExecuteButton")
        
        
class ForceLocalNodeTreeExecution(bpy.types.Operator):
    bl_idname = "mn.force_local_node_tree_execution"
    bl_label = "Force Local Node Tree Execution"
    
    nodeTreeName = bpy.props.StringProperty()
    nodeName = bpy.props.StringProperty()
        
    def execute(self, context):
        node = getNode(self.nodeTreeName, self.nodeName)
        forceExecution(sender = node)
        return {'FINISHED'}
