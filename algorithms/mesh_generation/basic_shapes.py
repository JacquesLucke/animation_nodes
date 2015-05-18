import math

def alignedCircleVertices(center, radius, resolution, directionX, directionY):
    vertices = []
    angleMultiplier = 2 * math.pi / resolution
    for i in range(resolution):
        angle = i * angleMultiplier
        vector = center + radius * math.cos(angle) * directionX + radius * math.sin(angle) * directionY
        vertices.append(vector)
    return vertices