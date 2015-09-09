import bpy
from .. base_types.socket import AnimationNodeSocket

class SequenceListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_SequenceListSocket"
    bl_label = "Sequence List Socket"
    dataType = "Sequence List"
    allowedInputTypes = ["Sequence List"]
    drawColor = (0.3, 0.644, 0.1, 1)
    storable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
