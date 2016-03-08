import bpy
from .. base_types.socket import AnimationNodeSocket

class VertexListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VertexListSocket"
    bl_label = "Vertex List Socket"
    dataType = "Vertex List"
    allowedInputTypes = ["Vertex List"]
    drawColor = (0.55, 0.61, 0.32, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[element.copy() for element in value]"
