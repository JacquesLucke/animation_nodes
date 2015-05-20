import bpy, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_AddSplinesToBezierCurve(Node, AnimationNode):
    bl_idname = "mn_AddSplinesToBezierCurve"
    bl_label = "Add Splines to Bezier Curve"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierCurveSocket", "Curve").showObjectInput = False
        self.inputs.new("mn_BezierSplineListSocket", "Splines").showName = False
        self.outputs.new("mn_BezierCurveSocket", "Curve")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        pass
        
    def getInputSocketNames(self):
        return {"Curve" : "curve",
                "Splines" : "splines"}
    def getOutputSocketNames(self):
        return {"Curve" : "curve"}
        
    def execute(self, curve, splines):
        curve.splines.extend(splines)
        return curve