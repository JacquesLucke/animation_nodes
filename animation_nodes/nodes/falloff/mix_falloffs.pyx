import bpy
from bpy.props import *
from ... base_types import AnimationNode
from . constant_falloff import ConstantFalloff
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

    mixFalloffList = BoolProperty(name = "Mix Falloff List", default = False,
        update = AnimationNode.refresh)

    def create(self):
        if self.mixFalloffList:
            self.newInput("Falloff List", "Falloffs", "falloffs")
        else:
            self.newInput("Falloff", "A", "a")
            self.newInput("Falloff", "B", "b")
            if self.mixType in useFactorTypes:
                self.newInput("Float", "Factor", "factor", value = 1).setRange(0, 1)
        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        row = layout.row(align = True)
        row.prop(self, "mixType", text = "")
        row.prop(self, "mixFalloffList", text = "", icon = "LINENUMBERS_ON")

    def getExecutionFunctionName(self):
        if self.mixFalloffList:
            return "execute_List"
        else:
            if self.mixType in useFactorTypes:
                return "execute_WithFactor"
            else:
                return "execute_WithoutFactor"

    def execute_List(self, falloffs):
        if len(falloffs) == 0:
            return ConstantFalloff(0)

        if self.mixType == "ADD":
            return AddFalloffs(falloffs)
        elif self.mixType == "MULTIPLY":
            return MultiplyFalloffs(falloffs)
        elif self.mixType == "MIN":
            return MinFalloffs(falloffs)
        elif self.mixType == "MAX":
            return MaxFalloffs(falloffs)

    def execute_WithFactor(self, a, b, factor):
        if self.mixType == "ADD":
            return AddTwoFalloffs(a, b, factor)
        raise Exception("should not happen")

    def execute_WithoutFactor(self, a, b):
        if self.mixType == "MULTIPLY":
            return MultiplyTwoFalloffs(a, b)
        elif self.mixType == "MIN":
            return MinTwoFalloffs(a, b)
        elif self.mixType == "MAX":
            return MaxTwoFalloffs(a, b)
        raise Exception("should not happen")


cdef class MixTwoFalloffsBase(CompoundFalloff):
    cdef:
        Falloff a, b
        double factor

    def __cinit__(self, Falloff a, Falloff b, double factor = 0):
        self.a = a
        self.b = b
        self.factor = factor

    cdef list getDependencies(self):
        return [self.a, self.b]

cdef class AddTwoFalloffs(MixTwoFalloffsBase):
    cdef double evaluate(self, double *dependencyResults):
        return dependencyResults[0] + self.factor * dependencyResults[1]

cdef class MultiplyTwoFalloffs(MixTwoFalloffsBase):
    cdef double evaluate(self, double *dependencyResults):
        return dependencyResults[0] * dependencyResults[1]

cdef class MinTwoFalloffs(MixTwoFalloffsBase):
    cdef double evaluate(self, double *dependencyResults):
        return min(dependencyResults[0], dependencyResults[1])

cdef class MaxTwoFalloffs(MixTwoFalloffsBase):
    cdef double evaluate(self, double *dependencyResults):
        return max(dependencyResults[0], dependencyResults[1])


cdef class MixFalloffsBase(CompoundFalloff):
    cdef list falloffs
    cdef int amount

    def __init__(self, list falloffs not None):
        self.falloffs = falloffs
        self.amount = len(falloffs)
        if self.amount == 0:
            raise Exception("at least one falloff required")

    cdef list getDependencies(self):
        return self.falloffs

cdef class AddFalloffs(MixFalloffsBase):
    cdef double evaluate(self, double *dependencyResults):
        cdef int i
        cdef double sum = 0
        for i in range(self.amount):
            sum += dependencyResults[i]
        return sum

cdef class MultiplyFalloffs(MixFalloffsBase):
    cdef double evaluate(self, double *dependencyResults):
        cdef int i
        cdef double product = 1
        for i in range(self.amount):
            product *= dependencyResults[i]
        return product

cdef class MinFalloffs(MixFalloffsBase):
    cdef double evaluate(self, double *dependencyResults):
        cdef int i
        cdef double minValue = dependencyResults[0]
        for i in range(1, self.amount):
            if dependencyResults[i] < minValue:
                minValue = dependencyResults[i]
        return minValue

cdef class MaxFalloffs(MixFalloffsBase):
    cdef double evaluate(self, double *dependencyResults):
        cdef int i
        cdef double maxValue = dependencyResults[0]
        for i in range(1, self.amount):
            if dependencyResults[i] > maxValue:
                maxValue = dependencyResults[i]
        return maxValue
