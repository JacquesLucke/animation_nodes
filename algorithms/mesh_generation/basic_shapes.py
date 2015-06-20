import math

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