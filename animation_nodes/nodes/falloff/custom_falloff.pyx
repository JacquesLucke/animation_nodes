import bpy
from ... base_types import AnimationNode
from ... data_structures cimport BaseFalloff, FloatList

class CustomFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_CustomFalloffNode"
    bl_label = "Custom Falloff"

    def create(self):
        self.newInput("Float List", "Strengths", "strengths")
        self.newInput("Float", "Fallback", "fallback", hide = True).setRange(0, 1)
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, strengths, fallback):
        return CustomFalloff(FloatList.fromValues(strengths), fallback)


cdef class CustomFalloff(BaseFalloff):
    cdef FloatList strengths
    cdef Py_ssize_t length
    cdef float fallback

    def __cinit__(self, FloatList strengths, float fallback):
        self.strengths = strengths
        self.length = strengths.length
        self.fallback = fallback
        self.clamped = False
        self.dataType = "None"

    cdef float evaluate(self, void *object, Py_ssize_t index):
        if index < self.length:
            return self.strengths[index]
        return self.fallback
