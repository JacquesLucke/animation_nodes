import bpy
from .. base_types.socket import AnimationNodeSocket

class NLAStripSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_NLAStripSocket"
    bl_label = "NLA Strip Socket"
    dataType = "NLAStrip"
    allowedInputTypes = ["NLAStrip"]
    drawColor = (0.25, 0.26, 0.19, 1)

    def getValueCode(self):
        return "None"
