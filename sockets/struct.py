import bpy
from .. data_structures.struct import Struct
from .. base_types.socket import AnimationNodeSocket

class StructSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_StructSocket"
    bl_label = "Struct Socket"
    dataType = "Struct"
    allowedInputTypes = ["Struct"]
    drawColor = (0.3, 0.3, 0.3, 1)
    storable = True
    comparable = False

    def getValueCode(self):
        return "animation_nodes.data_structures.struct.Struct()"

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"


class StructListSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_StructListSocket"
    bl_label = "Struct List Socket"
    dataType = "Struct List"
    baseDataType = "Struct"
    allowedInputTypes = ["Struct List"]
    drawColor = (0.3, 0.3, 0.3, 0.5)
    storable = True
    comparable = False

    def getValueCode(self):
        return "[]"

    @classmethod
    def getCopyExpression(cls):
        return "[element.copy() for element in value]"
