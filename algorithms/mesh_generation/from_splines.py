from ... data_structures.splines.bezier_spline import BezierSpline
from . indices_utils import gridQuadPolygonIndices, tubeQuadPolygonIndices
from . basic_shapes import tubeVertices

# Loft
###################################

def loftSplines(splines, nSplineSamples, nSurfaceSamples, type = "LINEAR", cyclic = False, smoothness = 1):
    if type == "BEZIER": sampleFunctionName = "getSamples"
    if type == "LINEAR": sampleFunctionName = "getLinearSamples"

    vertices = []
    samples = [spline.getSamples(nSplineSamples) for spline in splines]
    for points in zip(*samples):
        spline = BezierSpline.fromLocations(points)
        spline.isCyclic = cyclic
        if type == "BEZIER": spline.calculateSmoothHandles(smoothness)
        spline.updateSegments()
        function = getattr(spline, sampleFunctionName)
        vertices.extend(function(nSurfaceSamples + int(cyclic)))
        if cyclic: del vertices[-1]
      
    if cyclic:
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
            location, tangent = axis.projectExtended(point)
            axisSamples.append(location)
            tangents.append(tangent)
        
    vertices = tubeVertices(axisSamples, profileSamples, tangents, nSurfaceSamples)
    polygons = tubeQuadPolygonIndices(nSplineSamples, nSurfaceSamples)
    
    return vertices, polygons