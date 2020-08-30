import bpy
import cython
from mathutils import Vector
from ... math cimport Vector3
from ... utils.bvh import isInsideVolume
from ... base_types import AnimationNode
from ... data_structures cimport BaseFalloff
from . constant_falloff import ConstantFalloff

class MeshFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshFalloffNode"
    bl_label = "Mesh Falloff"

    def create(self):
        self.newInput("BVHTree", "BVHTree", "bvhTree")
        self.newInput("Float", "Size", "size")
        self.newInput("Float", "Falloff Width", "falloffWidth", value = 1)
        self.newInput("Boolean", "Use Surface", "useSurface", value = True)
        self.newInput("Boolean", "Use Volume", "useVolume", value = False)

        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, bvhTree, size, falloffWidth, useSurface, useVolume):
        if bvhTree is None: return ConstantFalloff(0)
        if not useSurface and not useVolume: return ConstantFalloff(0)
        return MeshFalloff(bvhTree, 1e10, size, falloffWidth, useSurface, useVolume)

cdef class MeshFalloff(BaseFalloff):
    cdef:
        bvhTree
        float factor
        bint useVolume
        bint useSurface
        double bvhMaxDistance
        float minDistance, maxDistance

    @cython.cdivision(True)
    def __cinit__(self, bvhTree, double bvhMaxDistance, float size, float falloffWidth,
                  bint useSurface, bint useVolume):
        self.bvhTree = bvhTree
        self.bvhMaxDistance = bvhMaxDistance
        self.useSurface = useSurface
        self.useVolume = useVolume
        if falloffWidth < 0:
            size += falloffWidth
            falloffWidth = -falloffWidth
        self.minDistance = size
        self.maxDistance = size + falloffWidth

        if self.minDistance == self.maxDistance:
            self.minDistance -= 0.00001
        self.factor = 1 / (self.maxDistance - self.minDistance)

        self.dataType = "LOCATION"
        self.clamped = True

    cdef float evaluate(self, void *value, Py_ssize_t index):
        cdef float distance
        cdef float strength
        cdef Vector3* v
        v = <Vector3*>value
        if self.useSurface and self.useVolume:
            strength = <float>isInsideVolume(self.bvhTree, Vector((v.x, v.y, v.z)))
            distance = calculateDistance(self, v)
            return max(distance, strength)
        elif self.useSurface:
            return calculateDistance(self, <Vector3*>value)
        elif self.useVolume:
            return <float>isInsideVolume(self.bvhTree, Vector((v.x, v.y, v.z)))

cdef inline float calculateDistance(MeshFalloff self, Vector3 *v):
    cdef float distance = self.bvhTree.find_nearest(Vector((v.x, v.y, v.z)), self.bvhMaxDistance)[3]
    if distance <= self.minDistance: return 1
    if distance <= self.maxDistance: return 1 - (distance - self.minDistance) * self.factor
    return 0
