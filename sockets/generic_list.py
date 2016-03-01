import bpy
from .. base_types.socket import AnimationNodeSocket

class GenericListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_GenericListSocket"
    bl_label = "GenericListSocket"
    dataType = "Generic List"
    allowedInputTypes = ["Generic List"]
    drawColor = (0.6, 0.3, 0.3, 0.5)
    storable = False
    hashable = False

    def getValueCode(self):
        return "[]"
