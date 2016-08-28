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
        self.newInput("Float", "Max Distance", "maxDistance", value = 5)
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, origin, minDistance, maxDistance):
        return PointDistanceFalloff(origin, minDistance, maxDistance)


cdef class PointDistanceFalloff(BaseFalloff):
    cdef:
        Vector3 origin
        double factor, minDistance, maxDistance

    def __cinit__(self, vector, double minDistance, double maxDistance):
        if minDistance == maxDistance: minDistance -= 0.00001
        self.factor = 1 / (maxDistance - minDistance)
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        toVector3(&self.origin, vector)
        self.dataType = "Location"
        self.clamped = True

    cdef double evaluate(self, void* value, long index):
        cdef double distance = distanceVec3(&self.origin, <Vector3*>value)
        if distance <= self.minDistance: return 1
        if distance <= self.maxDistance: return 1 - (distance - self.minDistance) * self.factor
        return 0
