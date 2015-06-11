from ... data_structures.splines.bezier_spline import BezierSpline
from ... data_structures.splines.poly_spline import PolySpline
from . indices_utils import gridQuadPolygonIndices, tubeQuadPolygonIndices
from . basic_shapes import tubeVertices

# Loft
###################################

def loftSplines(splines, 
                nSplineSamples, nSurfaceSamples, 
                type = "LINEAR", cyclic = False, smoothness = 1, 
                uniformConverterResolution = 100, splineDistributionType = "RESOLUTION", surfaceDistributionType = "RESOLUTION",
                startSurfaceParameter = 0.0, endSurfaceParameter = 1.0):
                
    vertices = []
    
    if splineDistributionType == "RESOLUTION":
        samples = [spline.getSamples(nSplineSamples) for spline in splines]
    elif splineDistributionType == "UNIFORM":
        samples = [spline.getUniformSamples(nSplineSamples, resolution = uniformConverterResolution) for spline in splines]
    
    for points in zip(*samples):
        if type == "BEZIER":
            spline = BezierSpline.fromLocations(points)
            spline.isCyclic = cyclic
            spline.calculateSmoothHandles(smoothness)
        elif type == "LINEAR":
            spline = PolySpline.fromLocations(points)
            spline.isCyclic = cyclic
        spline.update()
        
        amount = nSurfaceSamples + int(cyclic)
        
        if surfaceDistributionType == "RESOLUTION":
            vertices.extend(spline.getSamples(amount, start = startSurfaceParameter, end = endSurfaceParameter))
        elif surfaceDistributionType == "UNIFORM":
            vertices.extend(spline.getUniformSamples(amount, resolution = uniformConverterResolution, start = startSurfaceParameter, end = endSurfaceParameter))
            
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