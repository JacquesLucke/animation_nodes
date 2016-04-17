import bpy
from mathutils import Matrix
from .. base_types.socket import AnimationNodeSocket

class MatrixSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MatrixSocket"
    bl_label = "Matrix Socket"
    dataType = "Matrix"
    allowedInputTypes = ["Matrix"]
    drawColor = (1, 0.56, 0.3, 1)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return Matrix.Identity(4)

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"


class MatrixListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MatrixListSocket"
    bl_label = "Matrix List Socket"
    dataType = "Matrix List"
    baseDataType = "Matrix"
    allowedInputTypes = ["Matrix List"]
    drawColor = (1, 0.56, 0.3, 0.5)
    storable = True
    comparable = False

    @classmethod
    def getDefaultValue(cls):
        return []

    @classmethod
    def getDefaultValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"
