import bpy
from .. base_types.socket import AnimationNodeSocket

class MeshDataListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MeshDataListSocket"
    bl_label = "Mesh Data List Socket"
    dataType = "Mesh Data List"
    allowedInputTypes = ["Mesh Data List"]
    drawColor = (0.5, 0.6, 0.38, 1)

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[element.copy() for element in value]"
