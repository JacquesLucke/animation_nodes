import bpy
from .. base_types.socket import AnimationNodeSocket

class TextBlockListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_TextBlockListSocket"
    bl_label = "Text Block List Socket"
    dataType = "Text Block List"
    allowedInputTypes = ["Text Block List"]
    drawColor = (0.5, 0.5, 0.5, 0.5)
    storable = False
    hashable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
