import bpy
from .. base_types.socket import AnimationNodeSocket

class ShapeKeyListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ShapeKeyListSocket"
    bl_label = "Shape Key List Socket"
    dataType = "Shape Key List"
    allowedInputTypes = ["Shape Key List"]
    drawColor = (1.0, 0.6, 0.5, 0.5)
    storable = False
    hashable = False

    def getValueCode(self):
        return "[]"
