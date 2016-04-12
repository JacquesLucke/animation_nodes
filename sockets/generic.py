import bpy
from .. base_types.socket import AnimationNodeSocket

class GenericSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_GenericSocket"
    bl_label = "Generic Socket"
    dataType = "Generic"
    allowedInputTypes = ["all"]
    drawColor = (0.6, 0.3, 0.3, 1.0)
    storable = False
    comparable = False

    def getValueCode(self):
        return "None"


class GenericListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_GenericListSocket"
    bl_label = "GenericListSocket"
    dataType = "Generic List"
    allowedInputTypes = ["Generic List"]
    drawColor = (0.6, 0.3, 0.3, 0.5)
    storable = False
    comparable = False

    def getValueCode(self):
        return "[]"
