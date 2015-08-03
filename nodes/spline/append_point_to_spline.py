import bpy
from bpy.props import *
from ... events import propertyChanged
from ... base_types.node import AnimationNode

pointTypeItems = [
    ("POINT", "Point", "Add a normal point to the spline"),
    ("BEZIER_POINT", "Bezier Point", "Add a point with handles")]

class AppendPointToSpline(bpy.types.Node, AnimationNode):
    bl_idname = "an_AppendPointToSpline"
    bl_label = "Append Point to Spline"

    inputNames = { "Spline" : "spline",
                   "Point" : "point",
                   "Left Handle" : "leftHandle",
                   "Right Handle" : "rightHandle" }

    outputNames = { "Spline" : "spline" }

    def settingChanged(self, context):
        self.inputs["Left Handle"].hide = self.pointType != "BEZIER_POINT"
        self.inputs["Right Handle"].hide = self.pointType != "BEZIER_POINT"
        propertyChanged(self, context)

    pointType = EnumProperty(name = "Point Type", default = "POINT", items = pointTypeItems, update = settingChanged)

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline")
        self.inputs.new("an_VectorSocket", "Point")
        self.inputs.new("an_VectorSocket", "Left Handle")
        self.inputs.new("an_VectorSocket", "Right Handle")
        self.outputs.new("an_SplineSocket", "Spline")
        self.settingChanged(bpy.context)

    def draw_buttons(self, context, layout):
        layout.prop(self, "pointType", text = "")

    def execute(self, spline, point, leftHandle, rightHandle):
        if self.pointType == "BEZIER_POINT" and spline.type == "BEZIER":
            spline.appendBezierPoint(point, leftHandle, rightHandle)
        else:
            spline.appendPoint(point)
        spline.isChanged = True
        return spline
