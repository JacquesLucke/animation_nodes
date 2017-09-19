import bpy
from ... data_structures cimport BaseFalloff
from ... base_types import AnimationNode
from ... math cimport Vector3, setVector3, distanceVec3

class PointDistanceFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_PointDistanceFalloffNode"
    bl_label = "Point Distance Falloff"

    def create(self):
        self.newInput("Vector", "Origin", "origin")
        self.newInput("Float", "Size", "size")
        self.newInput("Float", "Falloff Width", "falloffWidth", value = 4)
        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, origin, size, falloffWidth):
        return PointDistanceFalloff(origin, size, falloffWidth)


cdef class PointDistanceFalloff(BaseFalloff):
    cdef:
        Vector3 origin
        float factor
        float minDistance, maxDistance

    def __cinit__(self, vector, float size, float falloffWidth):
        if falloffWidth < 0:
            size += falloffWidth
            falloffWidth = -falloffWidth
        self.minDistance = size
        self.maxDistance = size + falloffWidth

        if self.minDistance == self.maxDistance:
            self.minDistance -= 0.00001
        self.factor = 1 / (self.maxDistance - self.minDistance)
        setVector3(&self.origin, vector)

        self.dataType = "Location"
        self.clamped = True

    cdef float evaluate(self, void *value, Py_ssize_t index):
        return calcDistance(self, <Vector3*>value)

    cdef void evaluateList(self, void *values, Py_ssize_t startIndex,
                           Py_ssize_t amount, float *target):
        cdef Py_ssize_t i
        for i in range(amount):
            target[i] = calcDistance(self, <Vector3*>values + i)


cdef inline float calcDistance(PointDistanceFalloff self, Vector3 *v):
    cdef float distance = distanceVec3(&self.origin, v)
    if distance <= self.minDistance: return 1
    if distance <= self.maxDistance: return 1 - (distance - self.minDistance) * self.factor
    return 0
