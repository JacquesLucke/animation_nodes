import bpy
from ... base_types import AnimationNode

class GetSplineAdaptiveSamplesNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_GetSplineAdaptiveSamplesNode"
    bl_label = "Get Spline Adaptive Samples"
    errorHandlingType = "EXCEPTION"

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Float", "Resolution", "resolution", value = 10, minValue = 1e-5)
        self.newInput("Float", "Max Step", "maxStep", value = 1).setRange(1e-5, 1.0)

        self.newOutput("Float List", "Parameters", "parameters")
        self.newOutput("Vector List", "Locations", "locations")
        self.newOutput("Vector List", "Tangents", "tangents")
        self.newOutput("Vector List", "Normals", "normals")
        self.newOutput("Float List", "Radii", "radii")
        self.newOutput("Float List", "Tilts", "tilts", hide = True)
        self.newOutput("Float List", "Curvatures", "curvatures", hide = True)

    def getExecutionCode(self, required):
        yield "if spline.isEvaluable() and isinstance(spline, BezierSpline):"
        yield "    pass"
        if "normals" in required:
            yield "    spline.ensureNormals()"
        if len(required) != 0:
            yield "    _resolution = max(resolution, 1e-5)"
            yield "    _maxStep = max(maxStep, 1e-5)"
            yield "    parameters = spline.getAdaptiveParameters(1 / _resolution, _maxStep)"
        if "locations" in required:
            yield "    locations = spline.samplePoints(parameters, False, 'RESOLUTION')"
        if "tangents" in required:
            yield "    tangents = spline.sampleTangents(parameters, False, 'RESOLUTION')"
        if "normals" in required:
            yield "    normals = spline.sampleNormals(parameters, False, 'RESOLUTION')"
        if "radii" in required:
            yield "    _radii = spline.sampleRadii(parameters, False, 'RESOLUTION')"
            yield "    radii = DoubleList.fromValues(_radii)"
        if "tilts" in required:
            yield "    _tilts = spline.sampleTilts(parameters, False, 'RESOLUTION')"
            yield "    tilts = DoubleList.fromValues(_tilts)"
        if "curvatures" in required:
            yield "    _curvatures = spline.sampleCurvatures(parameters, False, 'RESOLUTION')"
            yield "    curvatures = DoubleList.fromValues(_curvatures)"
        yield "else:"
        yield "    self.raiseErrorMessage('Can not sample points. Only evaluable Bezier curves are supported.')"
