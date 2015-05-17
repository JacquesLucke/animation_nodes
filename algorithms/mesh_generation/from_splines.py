from ... data_structures.curve import BezierSpline, BezierPoint
from . indices_utils import gridQuadPolygonIndices

def loftSplines(splines, nSplineSamples, nSurfaceSamples, type = "LINEAR", cyclic = False, smoothness = 1):        
    samples = [spline.getSamples(nSplineSamples) for spline in splines]
    if cyclic: nSurfaceSamples += 1
    
    vertices = []
    if type == "BEZIER":
        for points in zip(*samples):
            spline = BezierSpline()
            for point in points:
                bezierPoint = BezierPoint.fromLocation(point)
                spline.points.append(bezierPoint)
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
        polygons = gridQuadPolygonIndices(nSplineSamples, nSurfaceSamples)
        for i in range(0, (nSplineSamples - 1) * nSurfaceSamples, nSurfaceSamples):
            polygons.append((i, i + nSurfaceSamples, i + 2 * nSurfaceSamples - 1, i + nSurfaceSamples - 1))
    else:
        polygons = gridQuadPolygonIndices(nSplineSamples, nSurfaceSamples)
            
    return vertices, polygons