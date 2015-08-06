import bpy
from bpy.props import *
from .. base_types.socket import AnimationNodeSocket

class EmptySocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EmptySocket"
    bl_label = "Empty Socket"
    dataType = "Empty"
    allowedInputTypes = ["all"]
    drawColor = (0.0, 0.0, 0.0, 0.0)

    passiveType = StringProperty(default = "")

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return None
