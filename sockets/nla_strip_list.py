import bpy
from .. base_types.socket import AnimationNodeSocket

class NLAStripListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_NLAStripListSocket"
    bl_label = "NLA Strip List Socket"
    dataType = "NLAStrip List"
    allowedInputTypes = ["NLAStrip List"]
    drawColor = (0.25, 0.26, 0.19, 0.5)

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
