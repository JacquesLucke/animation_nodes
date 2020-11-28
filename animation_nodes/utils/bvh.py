from random import random
from mathutils import Vector

# in some cases multiple tests have to done
# to reduce the probability for errors
direction1 = Vector((random(), random(), random())).normalized()
direction2 = Vector((random(), random(), random())).normalized()
direction3 = Vector((random(), random(), random())).normalized()

def isInsideVolume(bvhTree, vector):
    hits1 = countHits(bvhTree, vector, direction1)
    if hits1 == 0: return False
    if hits1 == 1: return True

    hits2 = countHits(bvhTree, vector, direction2)
    if hits1 % 2 == hits2 % 2:
        return hits1 % 2 == 1

    hits3 = countHits(bvhTree, vector, direction3)
    return hits3 % 2 == 1

def countHits(bvhTree, start, direction):
    hits = 0
    offset = direction * 0.0001
    location = bvhTree.ray_cast(start, direction)[0]

    while location is not None:
        hits += 1
        location = bvhTree.ray_cast(location + offset, direction)[0]

    return hits
