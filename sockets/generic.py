import bpy
from .. base_types.socket import AnimationNodeSocket

class GenericSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_GenericSocket"
    bl_label = "Generic Socket"
    dataType = "Generic"
    allowedInputTypes = ["all"]
    drawColor = (0.6, 0.3, 0.3, 0.7)
    storable = False

    def getValueCode(self):
        return "None"
