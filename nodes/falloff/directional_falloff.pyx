import bpy
from ... data_structures cimport BaseFalloff
from ... base_types.node import AnimationNode
from ... math cimport Vector3, toVector3, distancePointToPlane
from . constant_falloff import ConstantFalloff

class DirectionalFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DirectionalFalloffNode"
    bl_label = "Directional Falloff"

    def create(self):
        self.newInput("Vector", "Position", "position")
        self.newInput("Vector", "Direction", "direction")
        self.newInput("Float", "Size", "size")
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, position, direction, size):
        if size == 0:
            return ConstantFalloff(0)
        if size < 0:
            size = -size
            direction = -direction
        return DirectionalFalloff(position, direction, size)


cdef class DirectionalFalloff(BaseFalloff):
    cdef double size
    cdef Vector3 position, direction

    def __cinit__(self, position, direction, double size):
        assert size > 0
        toVector3(&self.position, position)
        toVector3(&self.direction, direction)
        self.size = size
        self.clamped = True
        self.dataType = "Location"

    cdef double evaluate(self, void* value, long index):
        cdef double distance = distancePointToPlane(&self.position, &self.direction, <Vector3*>value)
        cdef double result = 1 - distance / self.size
        if result < 0: return 0
        return result
