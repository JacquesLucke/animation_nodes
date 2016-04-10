import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

pointTypeItems = [
    ("POINT", "Point", "Add a normal point to the spline"),
    ("BEZIER_POINT", "Bezier Point", "Add a point with handles")]

class AppendPointToSplineNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_AppendPointToSplineNode"
    bl_label = "Append Point to Spline"

    def settingChanged(self, context):
        self.inputs["Left Handle"].hide = self.pointType != "BEZIER_POINT"
        self.inputs["Right Handle"].hide = self.pointType != "BEZIER_POINT"
        propertyChanged(self, context)

    pointType = EnumProperty(name = "Point Type", default = "POINT", items = pointTypeItems, update = settingChanged)

    def create(self):
        self.newInput("an_SplineSocket", "Spline", "spline").dataIsModified = True
        self.newInput("an_VectorSocket", "Point", "point")
        self.newInput("an_VectorSocket", "Left Handle", "leftHandle")
        self.newInput("an_VectorSocket", "Right Handle", "rightHandle")
        self.newOutput("an_SplineSocket", "Spline", "outSpline")
        self.settingChanged(bpy.context)

    def draw(self, layout):
        layout.prop(self, "pointType", text = "")

    def execute(self, spline, point, leftHandle, rightHandle):
        if self.pointType == "BEZIER_POINT" and spline.type == "BEZIER":
            spline.appendBezierPoint(point, leftHandle, rightHandle)
        else:
            spline.appendPoint(point)
        spline.isChanged = True
        return spline
