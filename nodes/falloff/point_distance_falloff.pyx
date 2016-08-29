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
        self.newInput("Float", "Min Value", "minValue", hide = True, value = 0).setRange(0, 1)
        self.newInput("Float", "Max Value", "maxValue", hide = True, value = 1).setRange(0, 1)
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, origin, minDistance, maxDistance, minValue, maxValue):
        return PointDistanceFalloff(origin, minDistance, maxDistance, minValue, maxValue)


cdef class PointDistanceFalloff(BaseFalloff):
    cdef:
        Vector3 origin
        double factor
        double minDistance, maxDistance
        double minValue, maxValue

    def __cinit__(self, vector, double minDistance, double maxDistance,
                                double minValue, double maxValue):
        if minDistance == maxDistance: minDistance -= 0.00001
        self.factor = (maxValue - minValue) / (maxDistance - minDistance)
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.minValue = minValue
        self.maxValue = maxValue
        toVector3(&self.origin, vector)
        self.dataType = "Location"
        self.clamped = 0 <= min(minValue, maxValue) <= max(minValue, maxValue) <= 1

    cdef double evaluate(self, void* value, long index):
        cdef double distance = distanceVec3(&self.origin, <Vector3*>value)
        if distance <= self.minDistance: return self.maxValue
        if distance <= self.maxDistance: return self.maxValue - (distance - self.minDistance) * self.factor
        return self.minValue
