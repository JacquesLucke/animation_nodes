import bpy
from bpy.props import *
from ... events import propertyChanged
from ... tree_info import keepNodeState
from ... base_types import AnimationNode

pointTypeItems = [
    ("POINT", "Point", "Add a normal point to the spline", "NONE", 0),
    ("BEZIER_POINT", "Bezier Point", "Add a point with handles", "NONE", 1)]

class AppendPointToSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AppendPointToSplineNode"
    bl_label = "Append Point to Spline"

    pointType = EnumProperty(name = "Point Type", default = "POINT",
        items = pointTypeItems, update = AnimationNode.updateSockets)

    def create(self):
        self.newInput("Spline", "Spline", "spline", dataIsModified = True)
        self.newInput("Vector", "Point", "point")
        if self.pointType == "BEZIER_POINT":
            self.newInput("Vector", "Left Handle", "leftHandle")
            self.newInput("Vector", "Right Handle", "rightHandle")
        self.newOutput("Spline", "Spline", "outSpline")

    def draw(self, layout):
        layout.prop(self, "pointType", text = "")

    def getExecutionFunctionName(self):
        if self.pointType == "POINT":
            return "execute_Point"
        elif self.pointType == "BEZIER_POINT":
            return "execute_BezierPoint"

    def execute_Point(self, spline, point):
        if spline.type == "BEZIER":
            spline.appendPoint(point, point, point)
        else:
            spline.appendPoint(point)
        spline.markChanged()
        return spline

    def execute_BezierPoint(self, spline, point, leftHandle, rightHandle):
        if self.pointType == "BEZIER_POINT" and spline.type == "BEZIER":
            spline.appendPoint(point, leftHandle, rightHandle)
        else:
            spline.appendPoint(point)
        spline.markChanged()
        return spline
