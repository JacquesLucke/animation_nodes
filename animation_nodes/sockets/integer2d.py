import bpy
from bpy.props import *
from .. events import propertyChanged
from .. data_structures import Int2List
from .. base_types import AnimationNodeSocket, CListSocket
from . implicit_conversion import registerImplicitConversion


class Integer2DSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_Integer2DSocket"
    bl_label = "Integer 2D Socket"
    dataType = "Integer 2D"
    drawColor = (0.35, 0.7, 1.0, 1)
    comparable = True
    storable = True

    value: IntVectorProperty(default = [0, 0], size = 2, update = propertyChanged, subtype = "XYZ")

    def drawProperty(self, layout, text, node):
        col = layout.column(align = True)
        if text != "": col.label(text = text)
        col.prop(self, "value", index = 0, text = "X")
        col.prop(self, "value", index = 1, text = "Y")

    def getValue(self):
        return tuple(self.value)

    def setProperty(self, data):
        self.value = data

    @classmethod
    def getDefaultValue(cls):
        return (0, 0)

    @classmethod
    def getDefaultValueCode(cls):
        return "(0, 0)"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, tuple) and len(value) == 2: return value, 0
        elif isinstance(value, (list, set)) and len(value) == 2: return tuple(value), 1
        else: return cls.getDefaultValue(), 2

registerImplicitConversion("Edge Indices", "Integer 2D", "value")
registerImplicitConversion("Integer 2D", "Edge Indices", "value")

class Integer2DListSocket(bpy.types.NodeSocket, CListSocket):
    bl_idname = "an_Integer2DListSocket"
    bl_label = "Integer 2D List Socket"
    dataType = "Integer 2D List"
    baseType = Integer2DSocket
    drawColor = (0.35, 0.7, 1.0, 0.5)
    storable = True
    comparable = False
    listClass = Int2List

from .. nodes.mesh.c_utils import convert_EdgeIndicesList_to_Int2List, convert_Int2List_to_EdgeIndicesList
registerImplicitConversion("Edge Indices List", "Integer 2D List", convert_EdgeIndicesList_to_Int2List)
registerImplicitConversion("Integer 2D List", "Edge Indices List", convert_Int2List_to_EdgeIndicesList)
