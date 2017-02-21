import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures cimport CompoundFalloff, Falloff

mixTypeItems = [
    ("ADD", "Add", "", "NONE", 0),
    ("MULTIPLY", "Multiply", "", "NONE", 1),
    ("MAX", "Max", "", "NONE", 2),
    ("MIN", "Min", "", "NONE", 3)]

useFactorTypes = {"ADD"}

class MixFalloffsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MixFalloffsNode"
    bl_label = "Mix Falloffs"

    mixType = EnumProperty(name = "Mix Type", items = mixTypeItems,
        default = "MAX", update = AnimationNode.refresh)

    def create(self):
        self.newInput("Falloff", "A", "a")
        self.newInput("Falloff", "B", "b")
        if self.mixType in useFactorTypes:
            self.newInput("Float", "Factor", "factor", value = 1).setRange(0, 1)
        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        layout.prop(self, "mixType", text = "")

    def getExecutionFunctionName(self):
        if self.mixType in useFactorTypes:
            return "execute_WithFactor"
        else:
            return "execute_WithoutFactor"

    def execute_WithFactor(self, a, b, factor):
        if self.mixType == "ADD":
            return AddFalloffs(a, b, factor)
        raise Exception("should not happen")

    def execute_WithoutFactor(self, a, b):
        if self.mixType == "MULTIPLY":
            return MultiplyFalloffs(a, b)
        elif self.mixType == "MIN":
            return MinFalloffs(a, b)
        elif self.mixType == "MAX":
            return MaxFalloffs(a, b)
        raise Exception("should not happen")


cdef class MixFalloffsBase(CompoundFalloff):
    cdef:
        Falloff a, b
        double factor

    def __cinit__(self, Falloff a, Falloff b, double factor = 0):
        self.a = a
        self.b = b
        self.factor = factor

    cdef list getDependencies(self):
        return [self.a, self.b]

cdef class AddFalloffs(MixFalloffsBase):
    cdef double evaluate(self, double* dependencyResults):
        return dependencyResults[0] + self.factor * dependencyResults[1]

cdef class MultiplyFalloffs(MixFalloffsBase):
    cdef double evaluate(self, double* dependencyResults):
        return dependencyResults[0] * dependencyResults[1]

cdef class MinFalloffs(MixFalloffsBase):
    cdef double evaluate(self, double* dependencyResults):
        return min(dependencyResults[0], dependencyResults[1])

cdef class MaxFalloffs(MixFalloffsBase):
    cdef double evaluate(self, double* dependencyResults):
        return max(dependencyResults[0], dependencyResults[1])
