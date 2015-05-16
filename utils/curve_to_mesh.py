import math

def generateLoftedSurface(spline1, spline2, splineSamples, surfaceSamples):
    samples1 = spline1.getSamples(splineSamples)
    samples2 = spline2.getSamples(splineSamples)
    
    vertices = []
    for start, end in zip(samples1, samples2):
        for i in range(surfaceSamples):
            influence = i / (surfaceSamples - 1)
            vertices.append(start * influence + end * (1 - influence))
            
    polygons = generatedPolygonGridIndices(splineSamples, surfaceSamples)
            
    return vertices, polygons
    
    
def generateRevolvedSurface_SameParameter(axis, profile, splineSamples, surfaceSamples):
    axisSamples = axis.getSamples(splineSamples)
    profileSamples = profile.getSamples(splineSamples)
    tangents = axis.getTangentSamples(splineSamples)

    vertices = []
    for center, profilePoint, tangent in zip(axisSamples, profileSamples, tangents):
        directionX = profilePoint - center
        radius = directionX.length
        directionY = tangent.cross(directionX).normalized()
        directionX.normalize()
        vertices.extend(generateCircleVertices(center, radius, surfaceSamples, directionX, directionY))
        
    polygons = []
    if surfaceSamples > 2: polygons.extend(generatedPolygonGridIndices(splineSamples, surfaceSamples))
    for i in range(0, (splineSamples - 1) * surfaceSamples, surfaceSamples):
        polygons.append((i, i + surfaceSamples, i + 2 * surfaceSamples - 1, i + surfaceSamples - 1))
    
    return vertices, polygons
    
def generatedPolygonGridIndices(width, height):
    polygons = []
    for i in range(0, (width - 1) * height, height):
        for j in range(i, i + height - 1):
            polygons.append((j, j + 1, j + height + 1, j + height))
    return polygons
    
def generateCircleVertices(center, radius, amount, directionX, directionY):
    vertices = []
    angleMultiplier = 2 * math.pi / amount
    for i in range(amount):
        angle = i * angleMultiplier
        vector = center + radius * math.cos(angle) * directionX + radius * math.sin(angle) * directionY
        vertices.append(vector)
    return vertices
        