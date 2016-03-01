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
    hashable = False

    def getValue(self):
        return Matrix.Identity(4)

    def getCopyExpression(self):
        return "value.copy()"
