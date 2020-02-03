import bpy
from bpy.props import *
from mathutils import Vector
from .. events import propertyChanged
from .. data_structures import Vector2DList
from .. base_types import AnimationNodeSocket, CListSocket
from . implicit_conversion import registerImplicitConversion

class Vector2DSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_Vector2DSocket"
    bl_label = "Vector 2D Socket"
    dataType = "Vector 2D"
    drawColor = (0.15, 0.45, 0.7, 1.0)
    storable = True
    comparable = True

    value: FloatVectorProperty(default = [0, 0], size = 2, update = propertyChanged, subtype = "XYZ")

    def drawProperty(self, layout, text, node):
        col = layout.column(align = True)
        if text != "": col.label(text = text)
        col.prop(self, "value", index = 0, text = "X")
        col.prop(self, "value", index = 1, text = "Y")

    def getValue(self):
        return Vector(self.value)

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value[:]

    @classmethod
    def getDefaultValue(cls):
        return Vector((0, 0))

    @classmethod
    def getCopyExpression(cls):
        return "value.copy()"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Vector) and len(value) == 2:
            return value, 0
        try:
            if len(value) == 2: return Vector(value), 1
        except:
            pass
        return cls.getDefaultValue(), 2

registerImplicitConversion("Vector", "Vector 2D", "Vector((value.x, value.y))")
registerImplicitConversion("Vector 2D", "Vector", "Vector((value.x, value.y, 0))")

class Vector2DListSocket(bpy.types.NodeSocket, CListSocket):
    bl_idname = "an_Vector2DListSocket"
    bl_label = "Vector 2D List Socket"
    dataType = "Vector 2D List"
    baseType = Vector2DSocket
    drawColor = (0.15, 0.45, 0.7, 0.5)
    storable = True
    comparable = False
    listClass = Vector2DList

from .. nodes.vector.c_utils import convert_Vector3DList_to_Vector2DList, convert_Vector2DList_to_Vector3DList
registerImplicitConversion("Vector List", "Vector 2D List", convert_Vector3DList_to_Vector2DList)
registerImplicitConversion("Vector 2D List", "Vector List", convert_Vector2DList_to_Vector3DList)
