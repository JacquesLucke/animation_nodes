import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.mesh_generation.from_splines import revolveProfileAroundAxis

projectionTypeItems = [
    ("PARAMETER", "Same Parameter", ""),
    ("PROJECT", "Project", "") ]

class RevolveSpline(bpy.types.Node, AnimationNode):
    bl_idname = "an_RevolveSpline"
    bl_label = "Revolve Spline"

    inputNames = { "Axis" : "axis",
                   "Profile" : "profile",
                   "Spline Samples" : "splineSamples",
                   "Surface Samples" : "surfaceSamples" }

    outputNames = { "Vertices" : "vertices",
                    "Polygons" : "polygons" }

    projectionType = EnumProperty(name = "Projection Type", default = "PROJECT", items = projectionTypeItems, update = propertyChanged)

    def create(self):
        self.inputs.new("an_SplineSocket", "Axis")
        self.inputs.new("an_SplineSocket", "Profile")
        socket = self.inputs.new("an_IntegerSocket", "Spline Samples")
        socket.setMinMax(2, 10000)
        socket.value = 16
        socket = self.inputs.new("an_IntegerSocket", "Surface Samples")
        socket.setMinMax(3, 10000)
        socket.value = 16
        self.outputs.new("an_VectorListSocket", "Vertices")
        self.outputs.new("an_PolygonIndicesListSocket", "Polygons")
        self.width += 20

    def draw_buttons(self, context, layout):
        layout.prop(self, "projectionType", text = "")

    def execute(self, axis, profile, splineSamples, surfaceSamples):
        def canExecute():
            if not axis.isEvaluable: return False
            if not profile.isEvaluable: return False
            if splineSamples < 2: return False
            if surfaceSamples < 3: return False
            return True

        axis.update()
        profile.update()

        if canExecute():
            vertices, polygons = revolveProfileAroundAxis(axis, profile, splineSamples, surfaceSamples, self.projectionType)
            return vertices, polygons
        else: return [], []
