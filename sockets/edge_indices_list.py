import bpy
from .. base_types.socket import AnimationNodeSocket

class EdgeIndicesListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EdgeIndicesListSocket"
    bl_label = "Edge Indices List Socket"
    dataType = "Edge Indices List"
    allowedInputTypes = ["Edge Indices List"]
    drawColor = (0, 0.55, 0.23, 1)
    
    def getValue(self):
        return []

    def getValueCode(self):
        return "[]"

    def getCopyStatement(self):
        return "[edgeIndices[:] for edgeIndices in value]"
