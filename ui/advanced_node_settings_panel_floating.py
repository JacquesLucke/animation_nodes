import bpy
from bpy.props import *
from .. tree_info import getNodeByIdentifier
from .. utils.blender_ui import getDpiFactor

class FloatingAdvancedPanel(bpy.types.Operator):
    bl_idname = "an.floating_advanced_node_settings_panel"
    bl_label = "Advanced Node Settings"

    nodeIdentifier = StringProperty(default = "")

    @classmethod
    def poll(cls, context):
        try: return context.active_node.isAnimationNode
        except: return False

    def check(self, context):
        return True

    def invoke(self, context, event):
        self.nodeIdentifier = context.active_node.identifier
        return context.window_manager.invoke_props_dialog(self, width = 250 * getDpiFactor())

    def draw(self, context):
        try:
            node = getNodeByIdentifier(self.nodeIdentifier)
            node.drawAdvanced(self.layout)
        except:
            self.layout.label("An error occured during drawing of the advanced panel", icon = "INFO")

    def execute(self, context):
        return {"INTERFACE"}
