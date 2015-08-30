import bpy
from .. base_types.socket import AnimationNodeSocket

class MatrixListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MatrixListSocket"
    bl_label = "Matrix List Socket"
    dataType = "Matrix List"
    allowedInputTypes = ["Matrix List"]
    drawColor = (1, 0.7, 0.2, 1)

    def getValueCode(self):
        return "[]"

    def getCopyStatement(self):
        return "[element.copy() for element in value]"
