import cython
from random import random
from mathutils import Vector
from ... math cimport Vector3
from ... data_structures cimport BaseFalloff, FloatList, Vector3DList

cdef class calculateMeshSurfaceFalloff(BaseFalloff):
    cdef:
        bvhTree
        bint useVolume
        bint invert
        float factor
        float minDistance, maxDistance
        double bvhMaxDistance

    @cython.cdivision(True)
    def __cinit__(self, bvhTreeInput, double bvhMaxDistanceInput, float size, float falloffWidth,
                  bint useVolumeInput, bint invertInput):
        self.bvhTree = bvhTreeInput
        self.bvhMaxDistance = bvhMaxDistanceInput
        self.useVolume = useVolumeInput
        self.invert = invertInput
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
        if self.useVolume:
            v = <Vector3*>value
            strength = hitsPerLocation(self.bvhTree, Vector((v.x, v.y, v.z)))
            distance = calculateDistance(self, v)
            strength = max(distance, strength)
            if self.invert: strength = 1 - strength
            return strength
        else:
            strength = calculateDistance(self, <Vector3*>value)
            if self.invert: strength = 1 - strength
            return strength

    cdef void evaluateList(self, void *values, Py_ssize_t startIndex, Py_ssize_t amount, float *target):
        cdef float distance
        cdef float strength
        cdef Vector3* v
        cdef Py_ssize_t i

        if self.useVolume:
            for i in range(amount):
                v = <Vector3*>values + i
                strength = hitsPerLocation(self.bvhTree, Vector((v.x, v.y, v.z)))
                distance = calculateDistance(self, v)
                strength = max(distance, strength)
                if self.invert: strength = 1 - strength
                target[i] = strength
        else:
            for i in range(amount):
                strength = calculateDistance(self, <Vector3*>values + i)
                if self.invert: strength = 1 - strength
                target[i] = strength

cdef inline float calculateDistance(calculateMeshSurfaceFalloff self, Vector3 *v):
    cdef float distance = self.bvhTree.find_nearest(Vector((v.x, v.y, v.z)), self.bvhMaxDistance)[3]
    if distance <= self.minDistance: return 1
    if distance <= self.maxDistance: return 1 - (distance - self.minDistance) * self.factor
    return 0


cdef class calculateMeshVolumeFalloff(BaseFalloff):
    cdef:
        bvhTree
        bint invert

    def __cinit__(self, bvhTreeInput, bint invertInput):
        self.bvhTree = bvhTreeInput
        self.invert = invertInput

        self.dataType = "LOCATION"
        self.clamped = True

    cdef float evaluate(self, void *value, Py_ssize_t index):
        return calculateStrength(self, <Vector3*>value)

    cdef void evaluateList(self, void *values, Py_ssize_t startIndex, Py_ssize_t amount, float *target):
        cdef Py_ssize_t i
        for i in range(amount):
            target[i] = calculateStrength(self, <Vector3*>values + i)

cdef inline float calculateStrength(calculateMeshVolumeFalloff self, Vector3 *v):
    cdef float strength = hitsPerLocation(self.bvhTree, Vector((v.x, v.y, v.z)))
    if self.invert:
        return 1 - strength
    return strength

cdef hitsPerLocation(bvhTree, vector):
    direction1 = Vector((random(), random(), random())).normalized()
    cdef Py_ssize_t hits1 = countHits(bvhTree, vector, direction1)
    if hits1 == 0: return False
    if hits1 == 1: return True

    direction2 = Vector((random(), random(), random())).normalized()
    cdef Py_ssize_t hits2 = countHits(bvhTree, vector, direction2)
    if hits1 % 2 == hits2 % 2:
        return hits1 % 2 == 1

    direction3 = Vector((random(), random(), random())).normalized()
    cdef Py_ssize_t hits3 = countHits(bvhTree, vector, direction3)
    return hits3 % 2 == 1

cdef countHits(bvhTree, start, direction):
    cdef Py_ssize_t hits = 0

    offset = direction * 0.0001
    location = bvhTree.ray_cast(start, direction)[0]

    while location is not None:
        hits += 1
        location = bvhTree.ray_cast(location + offset, direction)[0]

    return hits
