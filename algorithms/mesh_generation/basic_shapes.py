import math
from mathutils import Vector

def gridVertices(xDivisions, yDivisions, xDistance = 1, yDistance = 1, offset = Vector((0, 0, 0))):
    vertices = []
    append = vertices.append
    for x in range(xDivisions):
        for y in range(yDivisions):
            append(Vector((x * xDistance, y * yDistance, 0)) + offset)
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
