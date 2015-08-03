import bpy
from .. base_types.socket import AnimationNodeSocket

class StringListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_StringListSocket"
    bl_label = "String List Socket"
    dataType = "String List"
    allowedInputTypes = ["String List"]
    drawColor = (1, 1, 1, 0.4)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return []

    def getCopyValueFunctionString(self):
        return "return value[:]"
