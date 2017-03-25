import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types import AnimationNode
from ... data_structures.splines.poly_spline import PolySpline
from ... data_structures.splines.bezier_spline import BezierSpline

splineTypeItems = [
    ("BEZIER", "Bezier", "Each control point has two handles", "CURVE_BEZCURVE", 0),
    ("POLY", "Poly", "Linear interpolation between the spline points", "NOCURVE", 1)
]

class SplineFromPointsNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineFromPointsNode"
    bl_label = "Spline from Points"

    splineType = EnumProperty(name = "Spline Type", default = "BEZIER",
        items = splineTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Vector List", "Points", "points", dataIsModified = True)
        if self.splineType == "BEZIER":
            self.newInput("Vector List", "Left Handles", "leftHandles", dataIsModified = True)
            self.newInput("Vector List", "Right Handles", "rightHandles", dataIsModified = True)
        self.newInput("Boolean", "Cyclic", "cyclic", value = False)
        self.newOutput("Spline", "Spline", "spline")

    def draw(self, layout):
        layout.prop(self, "splineType", text = "")

    def getExecutionFunctionName(self):
        if self.splineType == "BEZIER":
            return "execute_Bezier"
        elif self.splineType == "POLY":
            return "execute_Poly"

    def execute_Bezier(self, points, leftHandles, rightHandles, cyclic):
        self.correctHandlesListIfNecessary(points, leftHandles)
        self.correctHandlesListIfNecessary(points, rightHandles)
        return BezierSpline(points, leftHandles, rightHandles, cyclic)

    def correctHandlesListIfNecessary(self, points, handles):
        if len(points) < len(handles):
            del handles[len(points):]
        elif len(points) > len(handles):
            handles += points[len(handles):]

    def execute_Poly(self, points, cyclic):
        return PolySpline(points, cyclic)
