from random import random
from mathutils import Vector

cdef float hitsPerLocation(bvhTree, vector):
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

    offset = direction * 0.000005
    location = bvhTree.ray_cast(start, direction)[0]

    while location is not None:
        hits += 1
        location = bvhTree.ray_cast(location + offset, direction)[0]

    return hits
