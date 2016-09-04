import bpy
cimport cython
from bpy.props import *
from libc.limits cimport LONG_MAX
from ... data_structures cimport BaseFalloff
from ... base_types import AnimationNode

maskTypeItems = [
    ("EVERY_NTH", "Every Nth", "", "NONE", 0)
]

class IndexMaskFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IndexMaskFalloffNode"
    bl_label = "Index Mask Falloff"

    maskType = EnumProperty(name = "Mask Type", items = maskTypeItems)

    def create(self):
        self.newInput("Integer", "Step", "step", value = 2, minValue = 1)
        self.newInput("Float", "Min", "minValue", value = 0).setRange(0, 1)
        self.newInput("Float", "Max", "maxValue", value = 1).setRange(0, 1)
        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        layout.prop(self, "maskType")

    def execute(self, step, minValue, maxValue):
        return IndexMaskFalloff(step, minValue, maxValue)


cdef class IndexMaskFalloff(BaseFalloff):
    cdef long step
    cdef double minValue, maxValue

    def __cinit__(self, step, double minValue, double maxValue):
        self.step = max(1, step % LONG_MAX)
        self.minValue = minValue
        self.maxValue = maxValue
        self.dataType = "All"

    @cython.cdivision(True)
    cdef double evaluate(self, void* object, long index):
        if index % self.step != 0:
            return self.minValue
        return self.maxValue
