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
    comparable = False

    def getValue(self):
        return MeshData([], [], [])

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"


class MeshDataListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MeshDataListSocket"
    bl_label = "Mesh Data List Socket"
    dataType = "Mesh Data List"
    baseDataType = "Mesh Data"
    allowedInputTypes = ["Mesh Data List"]
    drawColor = (0.3, 0.4, 0.18, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"
