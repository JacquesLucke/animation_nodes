import bpy
from ... base_types.node import AnimationNode
from ... data_structures cimport CompoundFalloff, Falloff, InterpolationBase

class InterpolateFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_InterpolateFalloffNode"
    bl_label = "Interpolate Falloff"

    def create(self):
        self.newInput("Falloff", "Falloff", "falloff")
        self.newInput("Interpolation", "Interpolation", "interpolation", defaultDrawType = "PROPERTY_ONLY")
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, falloff, interpolation):
        return InterpolateFalloff(falloff, interpolation)


cdef class InterpolateFalloff(CompoundFalloff):
    cdef:
        Falloff falloff
        InterpolationBase interpolation

    def __cinit__(self, Falloff falloff, InterpolationBase interpolation):
        self.falloff = falloff
        self.interpolation = interpolation
        self.requiresClampedInput = True

    cdef list getDependencies(self):
        return [self.falloff]

    cdef double evaluate(self, double* dependencyResults):
        return self.interpolation.evaluate(min(max(dependencyResults[0], 0), 1))
