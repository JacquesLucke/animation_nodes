import bpy
from ... base_types.node import AnimationNode
from ... algorithms.random cimport uniformRandomNumber
from ... data_structures cimport CompoundFalloff, Falloff

class MixFalloffsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixFalloffsNode"
    bl_label = "Mix Falloffs"

    def create(self):
        self.newInput("Float", "Factor", "factor")
        self.newInput("Falloff", "A", "a")
        self.newInput("Falloff", "B", "b")
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, factor, a, b):
        return AddFalloffs(a, b, factor)


cdef class AddFalloffs(CompoundFalloff):
    cdef:
        Falloff a, b
        double factor

    def __cinit__(self, Falloff a, Falloff b, double factor):
        self.a = a
        self.b = b
        self.factor = factor

    cdef list getDependencies(self):
        return [self.a, self.b]

    cdef double evaluate(self, double* dependencyResults):
        return dependencyResults[0] + self.factor * dependencyResults[1]
