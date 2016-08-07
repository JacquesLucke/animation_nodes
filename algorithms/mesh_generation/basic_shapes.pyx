import math
from mathutils import Vector
from ... data_structures.lists.complex_lists cimport Vector3DList

def gridVertices(int xDivisions, int yDivisions, float xDistance = 1, float yDistance = 1, offset = Vector((0, 0, 0))):
    assert xDivisions >= 0
    assert yDivisions >= 0
    cdef:
        float xOffset, yOffset, zOffset
        int x, y
    vertices = Vector3DList(length = xDivisions * yDivisions)
    xOffset, yOffset, zOffset = offset
    cdef int tmp
    for x in range(xDivisions):
        tmp = x * yDivisions
        for y in range(yDivisions):
            vertices.base.data[(tmp + y) * 3 + 0] = x * xDistance + xOffset
            vertices.base.data[(tmp + y) * 3 + 1] = y * yDistance + yOffset
            vertices.base.data[(tmp + y) * 3 + 2] = zOffset
    return vertices

def lineVertices(start, end, long steps):
    assert steps >= 2
    cdef:
        float _start[3]
        float _end[3]
        float stepsInverse = 1 / <float>(steps - 1)
        float startWeight, endWeight
        long i

    _start = start
    _end = end

    vertices = Vector3DList(length = steps)
    for i in range(steps):
        startWeight = i * (1 - stepsInverse)
        endWeight = i * stepsInverse
        vertices.base.data[i * 3 + 0] = _start[0] * startWeight + _end[0] * endWeight
        vertices.base.data[i * 3 + 1] = _start[1] * startWeight + _end[1] * endWeight
        vertices.base.data[i * 3 + 2] = _start[2] * startWeight + _end[2] * endWeight
    return vertices

def tubeVertices(centerPoints, ringPoints, tangents, resolution):
    vertices = []
    for center, pointOnCircle, tangent in zip(centerPoints, ringPoints, tangents):
        vertices.extend(alignedCircleVertices(center, pointOnCircle, tangent, resolution))
    return vertices

def alignedCircleVertices(center, pointOnCircle, tangent, resolution):
    dirX = pointOnCircle - center
    radius = dirX.length
    dirY = tangent.cross(dirX).normalized()
    dirX.normalize()

    vertices = []
    angleFactor = 2 * math.pi / resolution
    for i in range(resolution):
        angle = i * angleFactor
        vertex = center + radius * (math.cos(angle) * dirX + math.sin(angle) * dirY)
        vertices.append(vertex)
    return vertices
