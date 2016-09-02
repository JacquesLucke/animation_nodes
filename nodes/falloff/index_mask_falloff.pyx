import bpy
cimport cython
from libc.limits cimport LONG_MAX
from ... data_structures cimport BaseFalloff
from ... base_types.node import AnimationNode

class IndexMaskFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IndexMaskFalloffNode"
    bl_label = "Index Mask Falloff"

    def create(self):
        self.newInput("Integer", "Step", "step", value = 2, minValue = 1)
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, step):
        return IndexMaskFalloff(step)


cdef class IndexMaskFalloff(BaseFalloff):
    cdef long step

    def __cinit__(self, step):
        self.step = max(1, step % LONG_MAX)
        self.dataType = "All"

    @cython.cdivision(True)
    cdef double evaluate(self, void* object, long index):
        if index % self.step != 0:
            return 0
        return 1
