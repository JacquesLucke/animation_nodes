import bpy
from .. tree_info import getNodesByType

class DataInputPanel(bpy.types.Panel):
    bl_idname = "an_data_input_panel"
    bl_label = "Data Input"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "AN"

    def draw(self, context):
        layout = self.layout
        nodes = getNodesByType("an_DataInput")
        for node in nodes:
            if not node.showInViewport: continue
            socket = node.inputs[0]
            if not hasattr(socket, "drawAsProperty"): continue
            socket.drawAsProperty(layout, node.label)
