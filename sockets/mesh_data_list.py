import bpy
from .. base_types.socket import AnimationNodeSocket

class MeshDataListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MeshDataListSocket"
    bl_label = "Mesh Data List Socket"
    dataType = "Mesh Data List"
    allowedInputTypes = ["Mesh Data List"]
    drawColor = (0.3, 0.4, 0.18, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[element.copy() for element in value]"
