import bpy
import cython
from ... utils cimport bvh
from mathutils import Vector
from ... math cimport Vector3
from ... base_types import AnimationNode
from ... data_structures cimport BaseFalloff
from . constant_falloff import ConstantFalloff

class MeshFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MeshFalloffNode"
    bl_label = "Mesh Falloff"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("BVHTree", "BVHTree", "bvhTree")
        self.newInput("Float", "Size", "size")
        self.newInput("Float", "Falloff Width", "falloffWidth", value = 1)
        self.newInput("Boolean", "Use Surface", "useSurface", value = True)
        self.newInput("Boolean", "Use Volume", "useVolume", value = False)
        self.newInput("Boolean", "Invert", "invert", value = False)
        self.newInput("Float", "Max Distance", "bvhMaxDistance", minValue = 0, value = 1e6, hide = True)

        self.newOutput("Falloff", "Falloff", "falloff")

    def execute(self, bvhTree, size, falloffWidth, useSurface, useVolume, invert, bvhMaxDistance):
        if bvhTree is None: return ConstantFalloff(0)
        if not useSurface and not useVolume: return ConstantFalloff(0)
        return calculateMeshFalloff(bvhTree, bvhMaxDistance, size, falloffWidth, useSurface, useVolume, invert)

cdef class calculateMeshFalloff(BaseFalloff):
    cdef:
        bvhTree
        bint invert
        float factor
        bint useVolume
        bint useSurface
        double bvhMaxDistance
        float minDistance, maxDistance

    @cython.cdivision(True)
    def __cinit__(self, bvhTree, double bvhMaxDistance, float size, float falloffWidth,
                  bint useSurface, bint useVolume, bint invert):
        self.bvhTree = bvhTree
        self.bvhMaxDistance = bvhMaxDistance
        self.useSurface = useSurface
        self.useVolume = useVolume
        self.invert = invert
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
            strength = bvh.hitsPerLocation(self.bvhTree, Vector((v.x, v.y, v.z)))
            distance = calculateDistance(self, v)
            strength = max(distance, strength)
            if self.invert: return 1 - strength
            return strength
        elif self.useSurface:
            strength = calculateDistance(self, <Vector3*>value)
            if self.invert: return 1 - strength
            return strength
        elif self.useVolume:
            strength = bvh.hitsPerLocation(self.bvhTree, Vector((v.x, v.y, v.z)))
            if self.invert: return 1 - strength
            return strength

cdef inline float calculateDistance(calculateMeshFalloff self, Vector3 *v):
    cdef float distance = self.bvhTree.find_nearest(Vector((v.x, v.y, v.z)), self.bvhMaxDistance)[3]
    if distance <= self.minDistance: return 1
    if distance <= self.maxDistance: return 1 - (distance - self.minDistance) * self.factor
    return 0
