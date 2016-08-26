import bpy
from ... data_structures cimport BaseFalloff
from ... base_types.node import AnimationNode
from ... math cimport Vector3, toVector3, distanceVec3

class PointDistanceFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PointDistanceFalloffNode"
    bl_label = "Point Distance Falloff"

    def create(self):
        self.newInput("Vector", "Origin", "origin")
        self.newInput("Float", "Min Distance", "minDistance")
        self.newInput("Float", "Max Distance", "maxDistance")
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, origin, minDistance, maxDistance):
        return PointDistanceFalloff(origin, minDistance, maxDistance)


cdef class PointDistanceFalloff(BaseFalloff):
    cdef:
        Vector3 origin
        double minDistance, maxDistance
        double factor

    def __cinit__(self, vector, minDistance, maxDistance):
        toVector3(&self.origin, vector)
        if minDistance == maxDistance: minDistance -= 0.00001
        self.factor = 1 / (maxDistance - minDistance)
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.dataType = "Location"

    cdef double evaluate(self, void* object, long index):
        return (distanceVec3(&self.origin, <Vector3*>object) - self.minDistance) * self.factor
