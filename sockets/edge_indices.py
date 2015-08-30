import bpy
from .. base_types.socket import AnimationNodeSocket

class EdgeIndicesSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EdgeIndicesSocket"
    bl_label = "Edge Indices Socket"
    dataType = "Edge Indices"
    allowedInputTypes = ["Edge Indices"]
    drawColor = (1.0, 0.55, 0.23, 1)

    def getValueCode(self):
        return "(0, 1)"

    def getCopyStatement(self):
        return "value[:]"
