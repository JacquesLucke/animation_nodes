import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... math cimport Vector3, distanceVec3
from . constant_falloff import ConstantFalloff
from . interpolate_falloff import InterpolateFalloff
from ... data_structures cimport Spline, PolySpline, BaseFalloff

class SplineFalloffNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineFalloffNode"
    bl_label = "Spline Falloff"
    bl_width_default = 160

    resolution = IntProperty(name = "Resolution", default = 5, min = 2,
        description = "Poly spline segments per bezier spline segments")

    def create(self):
        self.newInput("Spline", "Spline", "spline",
            defaultDrawType = "PROPERTY_ONLY",
            dataIsModified = True)
        self.newInput("Float", "Distance", "distance", value = 0)
        self.newInput("Float", "Width", "width", value = 1, minValue = 0)
        self.newInput("Interpolation", "Interpolation", "interpolation",
            defaultDrawType = "PROPERTY_ONLY")

        self.newOutput("Falloff", "Falloff", "falloff")

    def drawAdvanced(self, layout):
        layout.prop(self, "resolution")

    def execute(self, spline, distance, width, interpolation):
        if not spline.isEvaluable():
            return ConstantFalloff(1)

        if spline.type == "POLY":
            falloffSpline = spline
        else:
            falloffSpline = PolySpline(spline.getSamples(self.resolution * (len(spline.points) - 1)))
            falloffSpline.cyclic = spline.cyclic

        falloff = SplineFalloff(falloffSpline, distance, width)
        return InterpolateFalloff(falloff, interpolation)


cdef class SplineFalloff(BaseFalloff):
    cdef Spline spline
    cdef float distance, width

    def __cinit__(self, Spline spline, float distance, float width):
        self.spline = spline
        self.distance = distance
        self.width = max(width, 0.000001)
        self.clamped = False
        self.dataType = "Location"

    cdef double evaluate(self, void *point, long index):
        cdef Vector3 closestPoint
        cdef float parameter = self.spline.project_LowLevel(<Vector3*>point)
        self.spline.evaluate_LowLevel(parameter, &closestPoint)
        cdef float distance = distanceVec3(<Vector3*>point, &closestPoint)

        if distance < self.distance:
            return 1.0
        elif distance > self.distance + self.width:
            return 0.0
        else:
            return 1.0 - (distance - self.distance) / self.width
