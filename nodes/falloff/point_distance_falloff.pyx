import bpy
from bpy.props import *
from ... events import propertyChanged
from ... data_structures cimport BaseFalloff
from ... base_types.node import AnimationNode
from ... math cimport Vector3, toVector3, distanceVec3

class PointDistanceFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PointDistanceFalloffNode"
    bl_label = "Point Distance Falloff"

    clamp = BoolProperty(name = "Clamp", update = propertyChanged, default = True)

    def create(self):
        self.newInput("Vector", "Origin", "origin")
        self.newInput("Float", "Min Distance", "minDistance")
        self.newInput("Float", "Max Distance", "maxDistance")
        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        layout.prop(self, "clamp")

    def execute(self, origin, minDistance, maxDistance):
        return PointDistanceFalloff(origin, minDistance, maxDistance, self.clamp)


cdef class PointDistanceFalloff(BaseFalloff):
    cdef:
        Vector3 origin
        double minDistance, maxDistance
        double factor
        bint clamp

    def __cinit__(self, vector, double minDistance, double maxDistance, bint clamp):
        toVector3(&self.origin, vector)
        if minDistance == maxDistance: minDistance -= 0.00001
        self.factor = 1 / (maxDistance - minDistance)
        self.minDistance = minDistance
        self.maxDistance = maxDistance
        self.clamp = clamp
        self.dataType = "Location"

    cdef double evaluate(self, void* value, long index):
        cdef double result = (distanceVec3(&self.origin, <Vector3*>value) - self.minDistance) * self.factor
        if self.clamp: return min(max(result, 0), 1)
        return result
