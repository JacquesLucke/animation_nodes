import bpy
from .. base_types.socket import AnimationNodeSocket

class VectorListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VectorListSocket"
    bl_label = "Vector List Socket"
    dataType = "Vector List"
    allowedInputTypes = ["Vector List"]
    drawColor = (0.3, 0.9, 1, 0.6)

    def getValueCode(self):
        return "[]"

    def getCopyStatement(self):
        return "[element.copy() for element in value]"
