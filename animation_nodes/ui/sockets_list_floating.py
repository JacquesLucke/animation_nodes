import bpy
from bpy.props import *
from . node_panel import drawSocketLists
from .. tree_info import getNodeByIdentifier
from .. utils.blender_ui import getDpiFactor

class FloatingNodePanel(bpy.types.Operator):
    bl_idname = "an.floating_node_panel"
    bl_label = "Floating Node Panel"

    nodeIdentifier = StringProperty(default = "")

    @classmethod
    def poll(cls, context):
        try: return context.active_node.isAnimationNode
        except: return False

    def check(self, context):
        return True

    def invoke(self, context, event):
        self.nodeIdentifier = context.active_node.identifier
        return context.window_manager.invoke_props_dialog(self, width = 350 * getDpiFactor())

    def draw(self, context):
        node = getNodeByIdentifier(self.nodeIdentifier)
        drawSocketLists(self.layout, node)
        try: pass
        except:
            self.layout.label("An error occured during drawing of the socket lists", icon = "INFO")

    def execute(self, context):
        return {"INTERFACE"}
