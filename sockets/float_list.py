import bpy
from .. base_types.socket import AnimationNodeSocket

class FloatListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "mn_FloatListSocket"
    bl_label = "Float List Socket"
    dataType = "Float List"
    allowedInputTypes = ["Float List", "Integer List"]
    drawColor = (0.4, 0.2, 0.9, 1.0)

    def drawInput(self, layout, node, text):
        layout.label(text)

    def getValue(self):
        return []

    def getCopyValueFunctionString(self):
        return "return value[:]"
