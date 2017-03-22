import bpy
from bpy.props import *
from .. events import propertyChanged
from .. data_structures import BaseFalloff, CompoundFalloff
from .. base_types import AnimationNodeSocket
from .. nodes.falloff.constant_falloff import ConstantFalloff

class FalloffSocket(bpy.types.NodeSocket, AnimationNodeSocket):
    bl_idname = "an_FalloffSocket"
    bl_label = "Falloff Socket"
    dataType = "Falloff"
    allowedInputTypes = ["Falloff"]
    drawColor = (0.32, 1, 0.18, 1)
    comparable = False
    storable = False

    value = FloatProperty(default = 1, soft_min = 0, soft_max = 1, update = propertyChanged)

    def drawProperty(self, layout, text, node):
        layout.prop(self, "value", text = text, slider = True)

    def getValue(self):
        return ConstantFalloff(self.value)

    def setProperty(self, data):
        self.value = data

    def getProperty(self):
        return self.value

    @classmethod
    def getDefaultValue(cls):
        return ConstantFalloff(1.0)

    @classmethod
    def correctValue(cls, value):
        if isinstance(value, BaseFalloff) or isinstance(value, CompoundFalloff):
            return value, 0
        return cls.getDefaultValue(), 2
