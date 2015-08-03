import bpy
from .. base_types.socket import AnimationNodeSocket

class VectorListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VectorListSocket"
    bl_label = "Vector List Socket"
    dataType = "Vector List"
    allowedInputTypes = ["Vector List"]
    drawColor = (0.3, 0.9, 1, 0.6)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return []

    def getCopyValueFunctionString(self):
        return "return [element.copy() for element in value]"
