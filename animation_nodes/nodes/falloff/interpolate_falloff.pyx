import bpy
from ... base_types import AnimationNode
from ... data_structures cimport CompoundFalloff, Falloff, Interpolation

class InterpolateFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InterpolateFalloffNode"
    bl_label = "Interpolate Falloff"

    def create(self):
        self.newInput("Falloff", "Falloff", "inFalloff")
        self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Falloff", "Falloff", "outFalloff")

    def execute(self, falloff, interpolation):
        return InterpolateFalloff(falloff, interpolation)


cdef class InterpolateFalloff(CompoundFalloff):
    cdef:
        Falloff falloff
        Interpolation interpolation

    def __cinit__(self, Falloff falloff, Interpolation interpolation):
        self.falloff = falloff
        self.interpolation = interpolation
        self.clamped = interpolation.clamped

    cdef list getDependencies(self):
        return [self.falloff]

    cdef list getClampingRequirements(self):
        return [True]

    cdef float evaluate(self, float *dependencyResults):
        return self.interpolation.evaluate(dependencyResults[0])

    cdef void evaluateList(self, float **dependencyResults, Py_ssize_t amount, float *target):
        cdef float *data = dependencyResults[0]
        cdef Py_ssize_t i
        for i in range(amount):
            target[i] = self.interpolation.evaluate(data[i])
