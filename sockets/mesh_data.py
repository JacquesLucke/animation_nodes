import bpy
from .. data_structures.mesh import MeshData
from .. base_types.socket import AnimationNodeSocket

class MeshDataSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MeshDataSocket"
    bl_label = "Mesh Data Socket"
    dataType = "Mesh Data"
    allowedInputTypes = ["Mesh Data"]
    drawColor = (0.3, 0.4, 0.18, 1)
    storable = True
    hashable = True

    def getValue(self):
        return MeshData([], [], [])

    def getCopyExpression(self):
        return "value.copy()"

    def drawSuggestionsMenu(self, layout):
        self.invokeNodeInsertion(layout, "an_SetMeshDataOnObjectNode", 1, "Set On Object")
