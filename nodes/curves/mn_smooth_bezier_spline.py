import bpy, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_SmoothBezierSpline(Node, AnimationNode):
    bl_idname = "mn_SmoothBezierSpline"
    bl_label = "Smooth Bezier Spline"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline").showObjectInput = False
        self.inputs.new("mn_FloatSocket", "Smoothness")
        self.outputs.new("mn_BezierSplineSocket", "Spline")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        pass
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Smoothness" : "smoothness"}
    def getOutputSocketNames(self):
        return {"Spline" : "spline"}
        
    def execute(self, spline, smoothness):
        spline.calculateSmoothHandles(smoothness)
        return spline