import bpy
from bpy.props import *
from .. tree_info import getNodeByIdentifier

class NodeSuggestionsMenu(bpy.types.Menu):
    bl_idname = "an_node_suggestions_menu"
    bl_label = "Node Suggestions"

    @classmethod
    def poll(cls, context):
        try: return context.active_node.isAnimationNode
        except: return False

    def draw(self, context):
        layout = self.layout
        node = context.active_node
        for i, socket in enumerate(node.outputs):
            if socket.hasNodeSuggestions:
                props = layout.operator("an.open_node_socket_suggestions_menu", text = socket.getDisplayedName(), icon = "DOT")
                props.nodeIdentifier = node.identifier
                props.socketIndex = i

class OpenNodeSocketSuggestionsMenu(bpy.types.Operator):
    bl_idname = "an.open_node_socket_suggestions_menu"
    bl_label = "Open Socket Suggestions"

    nodeIdentifier = StringProperty()
    socketIndex = IntProperty()

    def execute(self, context):
        drawMenu = getDrawMenuFunction(self.nodeIdentifier, self.socketIndex)
        context.window_manager.popup_menu(drawMenu, title = "Choose Next Node", icon = "PLUGIN")
        return {"FINISHED"}

def getDrawMenuFunction(nodeIdentifier, socketIndex):
    def drawMenu(self, context):
        node = getNodeByIdentifier(nodeIdentifier)
        socket = node.outputs[socketIndex]
        socket.drawSuggestionsMenu(self.layout)
    return drawMenu
