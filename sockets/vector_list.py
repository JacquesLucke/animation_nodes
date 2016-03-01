import bpy
from .. base_types.socket import AnimationNodeSocket

class VectorListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VectorListSocket"
    bl_label = "Vector List Socket"
    dataType = "Vector List"
    allowedInputTypes = ["Vector List"]
    drawColor = (0.15, 0.15, 0.8, 0.5)
    storable = True
    hashable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[element.copy() for element in value]"
