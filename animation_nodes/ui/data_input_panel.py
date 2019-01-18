import bpy
from .. utils.layout import writeText
from .. tree_info import getNodesByType

class DataInputPanel(bpy.types.Panel):
    bl_idname = "an_data_input_panel"
    bl_label = "Data Input"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "AN"

    def draw(self, context):
        layout = self.layout
        nodes = getNodesByType("an_ViewportInputNode")
        for node in nodes:
            box = layout.box()
            box.label(text = node.name + ":")
            for socket in node.outputs[:-1]:
                socket.drawSocket(box, text = socket.text, node = node, drawType = "TEXT_PROPERTY_OR_NONE")
