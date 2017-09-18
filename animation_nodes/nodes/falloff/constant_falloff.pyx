import bpy
from ... base_types import AnimationNode
from ... data_structures cimport BaseFalloff

class ConstantFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_ConstantFalloffNode"
    bl_label = "Constant Falloff"

    def create(self):
        self.newInput("Float", "Strength", "strength")
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, strength):
        return ConstantFalloff(strength)


cdef class ConstantFalloff(BaseFalloff):
    cdef float value

    def __cinit__(self, float value):
        self.value = value
        self.clamped = 0 <= value <= 1
        self.dataType = "None"

    cdef float evaluate(self, void *object, Py_ssize_t index):
        return self.value

    cdef void evaluateList(self, void *values, Py_ssize_t startIndex,
                           Py_ssize_t amount, float *target):
        cdef Py_ssize_t i
        for i in range(amount):
            target[i] = self.value
