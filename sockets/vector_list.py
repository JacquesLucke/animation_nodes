import bpy
from .. base_types.socket import AnimationNodeSocket

class VectorListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_VectorListSocket"
    bl_label = "Vector List Socket"
    dataType = "Vector List"
    allowedInputTypes = ["Vector List"]
    drawColor = (0.15, 0.15, 0.8, 0.5)

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "[element.copy() for element in value]"

    def toDebugString(self, value, maxRows):
        return "\n".join("({:>8.4f}, {:>8.4f}, {:>8.4f})".format(*vector) for vector in value[:maxRows])

    def drawSuggestionsMenu(self, layout):
        self.invokeNodeInsertion(layout, "an_CombineMeshDataNode", 0, "Combine Mesh Data")
