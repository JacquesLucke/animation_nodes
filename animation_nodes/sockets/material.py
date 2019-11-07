import bpy
from bpy.props import *
from bpy.types import Material
from .. events import propertyChanged
from .. base_types import AnimationNodeSocket, PythonListSocket

class MaterialSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MaterialSocket"
    bl_label = "Material Socket"
    dataType = "Material"
    drawColor = (0.75, 0.5, 0.4, 1)
    storable = False
    comparable = True

    material: PointerProperty(type = Material, update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop(self, "material", text = text)
        self.invokeFunction(row, node, "createMaterial", icon = "PLUS")

    def getValue(self):
        return self.material

    def setProperty(self, data):
        self.material = data

    def getProperty(self):
        return self.material

    @classmethod
    def getDefaultValue(cls):
        return None

    def createMaterial(self):
        self.material = bpy.data.materials.new("Material")

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, Material) or value is None:
            return value, 0
        return cls.getDefaultValue(), 2


class MaterialListSocket(bpy.types.NodeSocket, PythonListSocket):
    bl_idname = "an_MaterialListSocket"
    bl_label = "Material List Socket"
    dataType = "Material List"
    baseType = MaterialSocket
    drawColor = (0.75, 0.5, 0.4, 0.5)
    storable = False
    comparable = False

    @classmethod
    def getCopyExpression(cls):
        return "value[:]"

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, list):
            if all(isinstance(element, Material) or element is None for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
