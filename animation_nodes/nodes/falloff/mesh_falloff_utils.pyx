import cython
from random import random
from mathutils import Vector
from ... math cimport Vector3
from mathutils.bvhtree import BVHTree
from ... data_structures cimport BaseFalloff, FloatList, Vector3DList

@cython.cdivision(True)
def calculateMeshSurfaceFalloff(Vector3DList locations, bvhTree, float fallback, float size,
                                float falloffWidth, double bvhMaxDistance, bint invert):
    cdef float minDistance, maxDistance, factor
    if falloffWidth < 0:
        size += falloffWidth
        falloffWidth = -falloffWidth
    minDistance = size
    maxDistance = size + falloffWidth

    if minDistance == maxDistance:
        minDistance -= 0.00001
    factor = 1 / (maxDistance - minDistance)

    cdef Py_ssize_t locAmount = locations.length
    cdef FloatList strengths = FloatList.fromValue(0, length = locAmount)
    cdef Py_ssize_t i
    for i in range(locAmount):
        strengths.data[i] = normalizedDistancePerLocation(bvhTree, locations.data[i], minDistance, maxDistance,
                                                          factor, bvhMaxDistance, invert)
    return CustomFalloff(FloatList.fromValues(strengths), fallback)

cdef normalizedDistancePerLocation(bvhTree, Vector3 vector, float minDistance, float maxDistance,
                                   float factor, double bvhMaxDistance, bint invert):
    cdef float distance = bvhTree.find_nearest(Vector((vector.x, vector.y, vector.z)), bvhMaxDistance)[3]
    if invert:
        distance = linearCampInterpolation(distance, minDistance, maxDistance, 1, 0)
    else:
        distance = linearCampInterpolation(distance, minDistance, maxDistance, 0, 1)
    if distance <= minDistance: return 1
    if distance <= maxDistance: return 1 - (distance - minDistance) * factor
    return 0

@cython.cdivision(True)
cdef linearCampInterpolation(float x, float xMin, float xMax, float yMin, float yMax):
    cdef float y = yMin + (x - xMin)*(yMax - yMin) / (xMax - xMin)
    if y > 1: return 1
    return y


def calculateMeshVolumeFalloff(Vector3DList locations, bvhTree, float fallback, bint invert):
    cdef Py_ssize_t locAmount = locations.length
    cdef FloatList strengths = FloatList.fromValue(0, length = locAmount)
    cdef Py_ssize_t i
    if invert:
        for i in range(locAmount):
            strengths.data[i] = 1 - hitsPerLocation(bvhTree, locations.data[i])
    else:
        for i in range(locAmount):
            strengths.data[i] = hitsPerLocation(bvhTree, locations.data[i])
    return CustomFalloff(FloatList.fromValues(strengths), fallback)

cdef hitsPerLocation(bvhTree, Vector3 vector):
    pyVector = Vector((vector.x, vector.y, vector.z))

    direction1 = Vector((random(), random(), random())).normalized()
    cdef Py_ssize_t hits1 = countHits(bvhTree, pyVector, direction1)
    if hits1 == 0: return False
    if hits1 == 1: return True

    direction2 = Vector((random(), random(), random())).normalized()
    cdef Py_ssize_t hits2 = countHits(bvhTree, pyVector, direction2)
    if hits1 % 2 == hits2 % 2:
        return hits1 % 2 == 1

    direction3 = Vector((random(), random(), random())).normalized()
    cdef Py_ssize_t hits3 = countHits(bvhTree, pyVector, direction3)
    return hits3 % 2 == 1

cdef countHits(bvhTree, start, direction):
    cdef Py_ssize_t hits = 0

    offset = direction * 0.0001
    location = bvhTree.ray_cast(start, direction)[0]

    while location is not None:
        hits += 1
        location = bvhTree.ray_cast(location + offset, direction)[0]

    return hits


cdef class CustomFalloff(BaseFalloff):
    cdef FloatList strengths
    cdef Py_ssize_t length
    cdef float fallback

    def __cinit__(self, FloatList strengths, float fallback):
        self.strengths = strengths
        self.length = strengths.length
        self.fallback = fallback
        self.clamped = False
        self.dataType = "NONE"

    cdef float evaluate(self, void *object, Py_ssize_t index):
        if index < self.length:
            return self.strengths[index]
        return self.fallback
