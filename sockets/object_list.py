import bpy
from .. base_types.socket import AnimationNodeSocket

class ObjectListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_ObjectListSocket"
    bl_label = "Object List Socket"
    dataType = "Object List"
    allowedInputTypes = ["Object List"]
    drawColor = (0, 0, 0, 0.4)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return []

    def getCopyValueFunctionString(self):
        return "return value[:]"
