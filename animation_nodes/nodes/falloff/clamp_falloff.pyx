import bpy
from ... base_types import AnimationNode
from ... data_structures cimport CompoundFalloff, Falloff

class ClampFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ClampFalloffNode"
    bl_label = "Clamp Falloff"

    def create(self):
        self.newInput("Falloff", "Falloff", "inFalloff")
        self.newInput("Float", "Min", "MinValue", value = 0)
        self.newInput("Float", "Max", "MaxValue", value = 1)
        self.newOutput("Falloff", "Falloff", "outFalloff")

    def execute(self, falloff, minValue, maxValue):
        return ClampFalloff(falloff, minValue, maxValue)


cdef class ClampFalloff(CompoundFalloff):
    cdef:
        Falloff falloff
        float minValue, maxValue

    def __cinit__(self, Falloff falloff, float minValue, float maxValue):
        self.falloff = falloff
        self.minValue = minValue
        self.maxValue = maxValue
        self.clamped = 0 <= min(minValue, maxValue) <= max(minValue, maxValue) <= 1

    cdef list getDependencies(self):
        return [self.falloff]

    cdef float evaluate(self, float *dependencyResults):
        return max(min(dependencyResults[0], self.maxValue), self.minValue)

    cdef void evaluateList(self, float **dependencyResults, Py_ssize_t amount, float *target):
        cdef float *data = dependencyResults[0]
        cdef Py_ssize_t i
        for i in range(amount):
            target[i] = max(min(data[i], self.maxValue), self.minValue)
