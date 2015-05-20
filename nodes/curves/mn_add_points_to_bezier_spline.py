import bpy, bmesh
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_AddPointsToBezierSpline(Node, AnimationNode):
    bl_idname = "mn_AddPointToBezierSpline"
    bl_label = "Add Points to Bezier Spline"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline").showObjectInput = False
        self.inputs.new("mn_BezierPointListSocket", "Bezier Points")
        self.outputs.new("mn_BezierSplineSocket", "Spline")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        pass
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Bezier Points" : "points"}
    def getOutputSocketNames(self):
        return {"Spline" : "spline"}
        
    def execute(self, spline, points):
        spline.points.extend(points)
        return spline