import bpy
from .. data_structures import Int2List
from .. base_types import AnimationNodeSocket, CListSocket
from . implicit_conversion import registerImplicitConversion


class Int2Socket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_Int2Socket"
    bl_label = "Int2 Socket"
    dataType = "Int2"
    drawColor = (0.35, 0.7, 1.0, 1)
    comparable = True
    storable = True

    @classmethod
    def getDefaultValue(cls):
        return (0, 1)

    @classmethod
    def getDefaultValueCode(cls):
        return "(0, 1)"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, tuple) and len(value) == 2: return value, 0
        elif isinstance(value, (list, set)) and len(value) == 2: return tuple(value), 1
        else: return cls.getDefaultValue(), 2

registerImplicitConversion("Edge Indices", "Int2", "(value.x, value.y)")
registerImplicitConversion("Int2", "Edge Indices", "(value.x, value.y)")

class Int2ListSocket(bpy.types.NodeSocket, CListSocket):
    bl_idname = "an_Int2ListSocket"
    bl_label = "Int2 List Socket"
    dataType = "Int2 List"
    baseType = Int2Socket
    drawColor = (0.35, 0.7, 1.0, 0.5)
    storable = True
    comparable = False
    listClass = Int2List

from .. nodes.mesh.c_utils import convert_EdgeIndicesList_to_Int2List, convert_Int2List_to_EdgeIndicesList
registerImplicitConversion("Edge Indices List", "Int2 List", convert_EdgeIndicesList_to_Int2List)
registerImplicitConversion("Int2 List", "Edge Indices List", convert_Int2List_to_EdgeIndicesList)
