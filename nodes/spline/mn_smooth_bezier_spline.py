import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.splines.bezier_spline import BezierSpline
from ... data_structures.splines.poly_spline import PolySpline


class mn_SmoothBezierSpline(Node, AnimationNode):
    bl_idname = "mn_SmoothBezierSpline"
    bl_label = "Smooth Bezier Spline"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showObjectInput = False
        self.inputs.new("mn_FloatSocket", "Smoothness").number = 0.3333
        self.outputs.new("mn_SplineSocket", "Spline")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Smoothness" : "smoothness"}

    def getOutputSocketNames(self):
        return {"Spline" : "spline"}

    def execute(self, spline, smoothness):
        if spline.type == "BEZIER":
            spline.calculateSmoothHandles(smoothness)
            spline.isChanged = True
        return spline
