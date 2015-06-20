import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.splines.bezier_spline import BezierSpline
from ... data_structures.splines.poly_spline import PolySpline

pointTypeItems = [
    ("POINT", "Point", "Add a normal point to the spline"),
    ("BEZIER_POINT", "Bezier Point", "Add a point with handles")]

class mn_AppendPointToSpline(Node, AnimationNode):
    bl_idname = "mn_AppendPointToSpline"
    bl_label = "Append Point to Spline"
    
    def settingChanged(self, context):
        self.inputs["Left Handle"].hide = self.pointType != "BEZIER_POINT"
        self.inputs["Right Handle"].hide = self.pointType != "BEZIER_POINT"
        nodePropertyChanged(self, context)
    
    pointType = EnumProperty(name = "Point Type", default = "POINT", items = pointTypeItems, update = settingChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline")
        self.inputs.new("mn_VectorSocket", "Point")
        self.inputs.new("mn_VectorSocket", "Left Handle")
        self.inputs.new("mn_VectorSocket", "Right Handle")
        self.outputs.new("mn_SplineSocket", "Spline")
        self.settingChanged(context)
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "pointType", text = "")
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Point" : "point",
                "Left Handle" : "leftHandle",
                "Right Handle" : "rightHandle"}

    def getOutputSocketNames(self):
        return {"Spline" : "spline"}

    def execute(self, spline, point, leftHandle, rightHandle):
        if self.pointType == "BEZIER_POINT" and spline.type == "BEZIER":
            spline.appendBezierPoint(point, leftHandle, rightHandle)
        else:
            spline.appendPoint(point)
        spline.isChanged = True
        return spline
