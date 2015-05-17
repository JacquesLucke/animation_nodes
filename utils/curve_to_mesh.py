import math
from mathutils import Vector
from .. data_structures.curve import BezierSpline, BezierPoint

def generateLoftedSurface(splines, splineSamples, surfaceSamples, type = "LINEAR", smoothness = 1):
    samples = [spline.getSamples(splineSamples) for spline in splines]
    vertices = []
    
    if type == "BEZIER":
        for points in zip(*samples):
            spline = BezierSpline()
            for point in points:
                bezierPoint = BezierPoint()
                bezierPoint.location = point
                bezierPoint.leftHandle = point + Vector((1, 0, 0))
                bezierPoint.rightHandle = point + Vector((-1, 0, 0))
                spline.points.append(bezierPoint)
            spline.calculateSmoothHandles(smoothness)
            spline.updateSegments()
            vertices.extend(spline.getSamples(surfaceSamples))
            
    if type == "LINEAR":
        amount = len(splines)
        parameters = [min(i / (surfaceSamples - 1) * (amount - 1), amount - 1.00001) for i in range(surfaceSamples)]
        influences = [parameter - int(parameter) for parameter in parameters]
        pointIndices = [(int(parameter), int(parameter) + 1) for parameter in parameters]
        for points in zip(*samples):
            for (start, end), influence in zip(pointIndices, influences):
                vertices.append(points[start] * (1 - influence) + points[end] * influence)
            
    polygons = generatedPolygonGridIndices(splineSamples, surfaceSamples)
            
    return vertices, polygons
    
def generateRevolvedSurface_SameParameter(axis, profile, splineSamples, surfaceSamples):
    axisSamples = axis.getSamples(splineSamples)
    profileSamples = profile.getSamples(splineSamples)
    tangents = axis.getTangentSamples(splineSamples)
    return generateRevolvedSurface(axisSamples, profileSamples, tangents, surfaceSamples)
    
def generateRevolvedSurface(axisSamples, profileSamples, tangents, surfaceSamples):
    splineSamples = len(axisSamples)

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
        