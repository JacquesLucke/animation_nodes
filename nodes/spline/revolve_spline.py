import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... algorithms.mesh_generation.from_splines import revolveProfileAroundAxis

projectionTypeItems = [
    ("PARAMETER", "Same Parameter", ""),
    ("PROJECT", "Project", "") ]

class RevolveSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_RevolveSplineNode"
    bl_label = "Revolve Spline"
    bl_width_default = 160

    projectionType = EnumProperty(name = "Projection Type", default = "PROJECT",
        items = projectionTypeItems, update = propertyChanged)

    def create(self):
        self.newInput("Spline", "Axis", "axis")
        self.newInput("Spline", "Profile", "profile")
        self.newInput("Integer", "Spline Samples", "splineSamples", value = 16, minValue = 2)
        self.newInput("Integer", "Surface Samples", "surfaceSamples", value = 16, minValue = 3)
        self.newOutput("Vector List", "Vertices", "vertices")
        self.newOutput("Polygon Indices List", "Polygons", "polygons")

    def draw(self, layout):
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
