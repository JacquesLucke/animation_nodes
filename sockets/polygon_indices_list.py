import bpy
from .. base_types.socket import AnimationNodeSocket

class PolygonIndicesListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_PolygonIndicesListSocket"
    bl_label = "Polygon Indices List Socket"
    dataType = "Polygon Indices List"
    allowedInputTypes = ["Polygon Indices List"]
    drawColor = (0.6, 0.3, 0.8, 0.5)

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[polygonIndices[:] for polygonIndices in value]"

    def toDebugString(self, value, maxRows):
        return "\n".join(str(indices) for indices in value[:maxRows])
