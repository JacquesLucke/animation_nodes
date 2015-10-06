import bpy
from .. base_types.socket import AnimationNodeSocket

class EdgeIndicesListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_EdgeIndicesListSocket"
    bl_label = "Edge Indices List Socket"
    dataType = "Edge Indices List"
    allowedInputTypes = ["Edge Indices List"]
    drawColor = (0.4, 0.6, 0.6, 0.5)
    storable = True
    hashable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[edgeIndices[:] for edgeIndices in value]"

    def toDebugString(self, value, maxRows):
        return "\n".join(str(indices) for indices in value[:maxRows])
