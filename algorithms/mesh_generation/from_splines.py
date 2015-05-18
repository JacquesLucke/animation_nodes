from ... data_structures.curve import BezierSpline, BezierPoint
from . indices_utils import gridQuadPolygonIndices, tubeQuadPolygonIndices
from . basic_shapes import tubeVertices

# Loft
###################################

def loftSplines(splines, nSplineSamples, nSurfaceSamples, type = "LINEAR", cyclic = False, smoothness = 1):        
    samples = [spline.getSamples(nSplineSamples) for spline in splines]
    if cyclic: nSurfaceSamples += 1
    
    vertices = []
    if type == "BEZIER":
        for points in zip(*samples):
            spline = BezierSpline.fromLocations(points)
            spline.isCyclic = cyclic
            spline.calculateSmoothHandles(smoothness)
            spline.updateSegments()
            vertices.extend(spline.getSamples(nSurfaceSamples))
            if cyclic: del vertices[-1]
            
    if type == "LINEAR":
        amount = len(splines)
        if cyclic:
            amount += 1
            samples.append(samples[0])
        parameters = [min(i / (nSurfaceSamples - 1) * (amount - 1), amount - 1.00001) for i in range(nSurfaceSamples)]
        influences = [parameter - int(parameter) for parameter in parameters]
        pointIndices = [(int(parameter), int(parameter) + 1) for parameter in parameters]
        for points in zip(*samples):
            for (start, end), influence in zip(pointIndices, influences):
                vertices.append(points[start] * (1 - influence) + points[end] * influence)
            if cyclic: del vertices[-1]
      
    if cyclic:
        nSurfaceSamples -= 1
        polygons = tubeQuadPolygonIndices(nSplineSamples, nSurfaceSamples)
    else:
        polygons = gridQuadPolygonIndices(nSplineSamples, nSurfaceSamples)
            
    return vertices, polygons
 

# Revolve
################################### 
    
def revolveProfileAroundAxis(axis, profile, nSplineSamples, nSurfaceSamples, type = "PARAMETER"):
    if type == "PARAMETER":
        axisSamples = axis.getSamples(nSplineSamples)
        profileSamples = profile.getSamples(nSplineSamples)
        tangents = axis.getTangentSamples(nSplineSamples)
    if type == "PROJECT":
        profileSamples = profile.getSamples(nSplineSamples)
        axisSamples = []
        tangents = []
        for point in profileSamples:
            location, tangent = axis.findNearestPointAndTangentOnExtendedSpline(point)
            axisSamples.append(location)
            tangents.append(tangent)
        
    vertices = tubeVertices(axisSamples, profileSamples, tangents, nSurfaceSamples)
    polygons = tubeQuadPolygonIndices(nSplineSamples, nSurfaceSamples)
    
    return vertices, polygons