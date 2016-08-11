from . import grid
from . basic_shapes import tubeVertices
from ... data_structures.splines.poly_spline cimport PolySpline
from ... data_structures.splines.bezier_spline cimport BezierSpline
from ... data_structures.lists.complex_lists cimport Vector3DList

# Loft
###################################

def loftSplines(splines,
                nSplineSamples, nSurfaceSamples, *,
                type = "LINEAR", cyclic = False, smoothness = 0.333,
                uniformConverterResolution = 100, splineDistributionType = "RESOLUTION", surfaceDistributionType = "RESOLUTION",
                startSurfaceParameter = 0.0, endSurfaceParameter = 1.0):
    assert len(splines) >= 2
    assert nSplineSamples >= 2
    assert nSurfaceSamples >= 2

    def calculateVertices():
        vertices = Vector3DList()
        for samples in zip(*sampleInputSplines()):
            spline = createSurfaceSpline(Vector3DList.fromValues(samples))
            vertices.extend(sampleSurfaceSpline(spline))
        return vertices

    def sampleInputSplines():
        if splineDistributionType == "RESOLUTION":
            return [spline.getSamples(nSplineSamples)
                    for spline in splines]
        elif splineDistributionType == "UNIFORM":
            return [spline.getUniformSamples(nSplineSamples, resolution = uniformConverterResolution)
                    for spline in splines]

    def createSurfaceSpline(samples):
        if type == "BEZIER":
            spline = BezierSpline(samples, samples.copy(), samples.copy(), cyclic)
            spline.calculateSmoothHandles(smoothness)
        elif type == "LINEAR":
            spline = PolySpline(samples, cyclic)
        return spline

    def sampleSurfaceSpline(spline):
        if surfaceDistributionType == "RESOLUTION":
            return spline.getSamples(nSurfaceSamples,
                start = startSurfaceParameter, end = endSurfaceParameter)
        elif surfaceDistributionType == "UNIFORM":
            return spline.getUniformSamples(nSurfaceSamples,
                resolution = uniformConverterResolution,
                start = startSurfaceParameter, end = endSurfaceParameter)

    def calculatePolygonIndices():
        allSplinesCyclic = all(spline.cyclic for spline in splines)
        isRealCyclic = cyclic and startSurfaceParameter <= 0.0 and endSurfaceParameter >= 1.0
        return grid.quadPolygons(
                   nSplineSamples, nSurfaceSamples,
                   joinHorizontal = allSplinesCyclic,
                   joinVertical = isRealCyclic)

    return calculateVertices(), calculatePolygonIndices()


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
    polygons = grid.quadPolygons(nSplineSamples, nSurfaceSamples, joinVertical = True)

    return vertices, polygons
