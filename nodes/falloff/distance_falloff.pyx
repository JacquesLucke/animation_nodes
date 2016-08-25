import bpy
from ... data_structures cimport FalloffBase
from ... base_types.node import AnimationNode
from ... math cimport Vector3, toVector3, distanceVec3

class DistanceFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_DistanceFalloffNode"
    bl_label = "Distance Falloff"

    def create(self):
        self.newInput("Vector", "Origin", "origin")
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, origin):
        return DistanceFalloff(origin)


cdef class DistanceFalloff(FalloffBase):
    cdef Vector3 origin

    def __cinit__(self, vector):
        toVector3(&self.origin, vector)

    cpdef getHandledDataType(self):
        return "Location"

    cdef double execute(self, void* object, long index):
        return distanceVec3(&self.origin, <Vector3*>object)
