import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... data_structures import Vector3DList

splineTypeItems = [
    ("BEZIER", "Bezier", "Each control point has two handles", "CURVE_BEZCURVE", 0),
    ("POLY", "Poly", "Linear interpolation between the spline points", "NOCURVE", 1)
]

class SplineInfoNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_SplineInfoNode"
    bl_label = "Spline Info"

    splineType = EnumProperty(name = "Spline Type", default = "BEZIER",
        items = splineTypeItems, update = AnimationNode.refresh)

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY", dataIsModified = True)
        self.newOutput("Boolean", "Cyclic", "cyclic")
        self.newOutput("Vector List", "Points", "points")
        if self.splineType == "BEZIER":
            self.newOutput("Vector List", "Left Handles", "leftHandles")
            self.newOutput("Vector List", "Right Handles", "rightHandles")

    def draw(self, layout):
        layout.prop(self, "splineType", text = "")

    def getExecutionFunctionName(self):
        if self.splineType == "BEZIER":
            return "execute_Bezier"
        elif self.splineType == "POLY":
            return "execute_Poly"

    def execute_Bezier(self, spline):
        if spline.type == "BEZIER":
            return spline.cyclic, spline.points, spline.leftHandles, spline.rightHandles
        return spline.cyclic, spline.points, Vector3DList(), Vector3DList()

    def execute_Poly(self, spline):
        return spline.cyclic, spline.points
