import bpy
cimport cython
from ... utils.clamp cimport clampLong
from ... base_types.node import AnimationNode
from ... data_structures cimport BaseFalloff, Interpolation

class FadeFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_FadeFalloffNode"
    bl_label = "Fade Falloff"
    bl_width_default = 150

    def create(self):
        self.newInput("Integer", "Start Index", "startIndex", value = 0)
        self.newInput("Integer", "End Index", "endIndex", value = 10)
        self.newInput("Float", "Start Value", "startValue", value = 1)
        self.newInput("Float", "End Value", "endValue", value = 0)
        self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")

        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, startIndex, endIndex, startValue, endValue, interpolation):
        return FadeFalloff(startIndex, endIndex, startValue, endValue, interpolation)

cdef class FadeFalloff(BaseFalloff):
    cdef:
        long startIndex, endIndex
        double indexDiff
        double startValue, endValue
        Interpolation interpolation

    def __cinit__(self, startIndex, endIndex, startValue, endValue, interpolation):
        self.startIndex = clampLong(startIndex)
        self.endIndex = clampLong(endIndex)
        self.indexDiff = <double>(self.endIndex - self.startIndex)
        self.startValue = startValue
        self.endValue = endValue
        self.interpolation = interpolation
        self.clamped = True
        self.dataType = "All"

    @cython.cdivision(True)
    cdef double evaluate(self, void *object, long index):
        if index <= self.startIndex: return self.startValue
        if index >= self.endIndex: return self.endValue
        # indexDiff cannot be zero when this point is reached
        cdef double influence = <double>(index - self.startIndex) / self.indexDiff
        influence = self.interpolation.evaluate(influence)
        return self.startValue * (1 - influence) + self.endValue * influence
