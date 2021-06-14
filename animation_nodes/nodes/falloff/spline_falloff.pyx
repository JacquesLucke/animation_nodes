import bpy
from bpy.props import *
from ... events import propertyChanged
from ... math cimport Vector3, distanceVec3
from ... base_types import AnimationNode, VectorizedSocket
from ... data_structures cimport Spline, PolySpline, BaseFalloff

from . mix_falloffs import MixFalloffs
from . constant_falloff import ConstantFalloff
from . interpolate_falloff import InterpolateFalloff

mixListTypeItems = [
    ("MAX", "Max", "", "NONE", 0),
    ("ADD", "Add", "", "NONE", 1)
]

falloffTypeItems = [
    ("DISTANCE", "Distance", "", "NONE", 0),
    ("PARAMETER", "Parameter", "", "NONE", 1),
]

class SplineFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineFalloffNode"
    bl_label = "Spline Falloff"
    bl_width_default = 160

    __annotations__ = {}

    __annotations__["resolution"] = IntProperty(name = "Resolution", default = 5, min = 2,
        description = "Poly spline segments per bezier spline segments")

    __annotations__["falloffType"] = EnumProperty(name = "Falloff Type", default = "DISTANCE",
        items = falloffTypeItems, update = AnimationNode.refresh)

    __annotations__["mixListType"] = EnumProperty(name = "Mix List Type", default = "MAX",
        items = mixListTypeItems, update = propertyChanged)

    __annotations__["useSplineList"] = VectorizedSocket.newProperty()

    def create(self):
        socketProps = dict(defaultDrawType = "PROPERTY_ONLY", dataIsModified = True)
        self.newInput(VectorizedSocket("Spline", "useSplineList",
            ("Spline", "spline", socketProps),
            ("Splines", "splines", socketProps)))

        if self.falloffType == "DISTANCE":
            self.newInput("Boolean", "Use Radius for Distance", "useSplineRadiusForDistance", value = False)
            self.newInput("Float", "Distance", "distance", value = 0)
            self.newInput("Boolean", "Use Radius for Width", "useSplineRadiusForWidth", value = False)
            self.newInput("Float", "Width", "width", value = 1, minValue = 0)

        self.newInput("Interpolation", "Interpolation", "interpolation",
            defaultDrawType = "PROPERTY_ONLY")

        self.newOutput("Falloff", "Falloff", "falloff")

    def draw(self, layout):
        layout.prop(self, "falloffType", text = "")
        if self.useSplineList:
            layout.prop(self, "mixListType", text = "")

    def drawAdvanced(self, layout):
        layout.prop(self, "resolution")

    def getExecutionFunctionName(self):
        if self.falloffType == "DISTANCE":
            if self.useSplineList:
                return "execute_ListDistance"
            else:
                return "execute_SingleDistance"
        else:
            if self.useSplineList:
                return "execute_ListParameter"
            else:
                return "execute_SingleParameter"

    def execute_SingleDistance(self, spline, useSplineRadiusForDistance, distance, useSplineRadiusForWidth, width, interpolation):
        falloff = self.distanceFalloffFromSpline(spline, useSplineRadiusForDistance, distance, useSplineRadiusForWidth, width)
        return InterpolateFalloff(falloff, interpolation)

    def execute_ListDistance(self, splines, useSplineRadiusForDistance, distance, useSplineRadiusForWidth, width, interpolation):
        falloffs = []
        for spline in splines:
            if spline.isEvaluable():
                falloffs.append(self.distanceFalloffFromSpline(spline, useSplineRadiusForDistance, distance, useSplineRadiusForWidth, width))

        if self.mixListType == "ADD":
            interpolatedFalloffs = [InterpolateFalloff(f, interpolation) for f in falloffs]
            return MixFalloffs(interpolatedFalloffs, "ADD", default = 0)
        elif self.mixListType == "MAX":
            falloff = MixFalloffs(falloffs, "MAX", default = 0)
            return InterpolateFalloff(falloff, interpolation)

    def execute_SingleParameter(self, spline, interpolation):
        falloff = self.parameterFalloffFromSpline(spline)
        return InterpolateFalloff(falloff, interpolation)

    def execute_ListParameter(self, splines, interpolation):
        falloffs = []
        for spline in splines:
            if spline.isEvaluable():
                falloffs.append(self.parameterFalloffFromSpline(spline))

        if self.mixListType == "ADD":
            interpolatedFalloffs = [InterpolateFalloff(f, interpolation) for f in falloffs]
            return MixFalloffs(interpolatedFalloffs, "ADD", default = 0)
        elif self.mixListType == "MAX":
            falloff = MixFalloffs(falloffs, "MAX", default = 0)
            return InterpolateFalloff(falloff, interpolation)

    def distanceFalloffFromSpline(self, spline, useSplineRadiusForDistance, distance, useSplineRadiusForWidth, width):
        if not spline.isEvaluable():
            return ConstantFalloff(0)

        if spline.type == "POLY":
            falloffSpline = spline
        else:
            if useSplineRadiusForDistance or useSplineRadiusForWidth:
                falloffSpline = PolySpline(spline.getDistributedPoints(self.resolution * (len(spline.points) - 1)),
                                           spline.getDistributedRadii(self.resolution * (len(spline.points) - 1)))
            else:
                falloffSpline = PolySpline(spline.getDistributedPoints(self.resolution * (len(spline.points) - 1)))
            falloffSpline.cyclic = spline.cyclic

        return SplineDistanceFalloff(falloffSpline, useSplineRadiusForDistance, distance, useSplineRadiusForWidth, width)

    def parameterFalloffFromSpline(self, spline):
        if not spline.isEvaluable():
            return ConstantFalloff(0)

        if spline.type == "POLY":
            falloffSpline = spline
        else:
            falloffSpline = PolySpline(spline.getDistributedPoints(self.resolution * (len(spline.points) - 1)))
            falloffSpline.cyclic = spline.cyclic

        return SplineParameterFalloff(falloffSpline)


cdef class SplineDistanceFalloff(BaseFalloff):
    cdef Spline spline
    cdef float distance, width
    cdef bint useSplineRadiusForDistance, useSplineRadiusForWidth

    def __cinit__(self, Spline spline, bint useSplineRadiusForDistance, float distance, bint useSplineRadiusForWidth, float width):
        self.spline = spline
        self.useSplineRadiusForDistance = useSplineRadiusForDistance
        self.distance = distance
        self.useSplineRadiusForWidth = useSplineRadiusForWidth
        self.width = width
        self.clamped = False
        self.dataType = "LOCATION"

    cdef float evaluate(self, void *point, Py_ssize_t index):
        cdef Vector3 closestPoint
        cdef float parameter = self.spline.project_LowLevel(<Vector3*>point)
        self.spline.evaluatePoint_LowLevel(parameter, &closestPoint)
        cdef float distance = distanceVec3(<Vector3*>point, &closestPoint)
        cdef float _distance = self.distance
        cdef float _width = self.width
        cdef float radius
        if self.useSplineRadiusForDistance or self.useSplineRadiusForWidth:
            radius = self.spline.evaluateRadius_LowLevel(parameter)
            if self.useSplineRadiusForDistance: _distance *= radius
            if self.useSplineRadiusForWidth: _width *= radius

        _width = max(_width, 0.000001)
        if distance < _distance:
            return 1.0
        elif distance > _distance + _width:
            return 0.0
        else:
            return 1.0 - (distance - _distance) / _width

cdef class SplineParameterFalloff(BaseFalloff):
    cdef Spline spline

    def __cinit__(self, Spline spline):
        self.spline = spline
        self.clamped = True
        self.dataType = "LOCATION"

    cdef float evaluate(self, void *point, Py_ssize_t index):
        return self.spline.project_LowLevel(<Vector3*>point)
