import bpy
from bpy.props import *
from .. events import propertyChanged
from .. base_types import AnimationNodeSocket, PythonListSocket

class MaterialSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_MaterialSocket"
    bl_label = "Material Socket"
    dataType = "Material"
    drawColor = (0.75, 0.5, 0.4, 1)
    storable = False
    comparable = True

    materialName = StringProperty(update = propertyChanged)

    def drawProperty(self, layout, text, node):
        row = layout.row(align = True)
        row.prop_search(self, "materialName",  bpy.data, "materials", text = text)
        self.invokeFunction(row, node, "createMaterial", icon = "ZOOMIN")

    def getValue(self):
        return bpy.data.materials.get(self.materialName)

    def setProperty(self, data):
        self.materialName = data

    def getProperty(self):
        return self.materialName

    @classmethod
    def getDefaultValue(cls):
        return None

    def createMaterial(self):
        material = bpy.data.materials.new("Material")
        self.materialName = material.name

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, bpy.types.Material) or value is None:
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
            if all(isinstance(element, bpy.types.Material) or element is None for element in value):
                return value, 0
        return cls.getDefaultValue(), 2
