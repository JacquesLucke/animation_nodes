import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode
from ... data_structures.splines.poly_spline import PolySpline
from ... data_structures.splines.bezier_spline import BezierSpline

splineTypeItems = [
    ("BEZIER", "Bezier", "Each control point has two handles"),
    ("POLY", "Poly", "Linear interpolation between the spline points")]

class SplineFromPointsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineFromPointsNode"
    bl_label = "Spline from Points"

    splineType = EnumProperty(name = "Spline Type", default = "POLY",
        items = splineTypeItems, update = propertyChanged)

    def create(self):
        self.newInput("Vector List", "Points", "points")
        self.newInput("Boolean", "Cyclic", "cyclic", value = False)
        self.newOutput("Spline", "Spline", "spline")

    def draw(self, layout):
        layout.prop(self, "splineType", text = "")

    def execute(self, points, cyclic):
        if self.splineType == "BEZIER": spline = BezierSpline()
        if self.splineType == "POLY":
            spline = PolySpline(points)
            spline.cyclic = cyclic
        return spline
