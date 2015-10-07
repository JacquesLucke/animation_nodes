import bpy
from .. base_types.socket import AnimationNodeSocket

class ObjectGroupListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_ObjectGroupListSocket"
    bl_label = "Object Group List Socket"
    dataType = "Object Group List"
    allowedInputTypes = ["Object Group List"]
    drawColor = (0.3, 0.1, 0.1, 0.5)
    storable = False
    hashable = False

    def getValueCode(self):
        return "[]"

    def getCopyExpression(self):
        return "value[:]"
