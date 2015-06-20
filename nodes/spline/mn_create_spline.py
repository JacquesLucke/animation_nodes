import bpy
from bpy.types import Node
from bpy.props import *
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.splines.bezier_spline import BezierSpline
from ... data_structures.splines.poly_spline import PolySpline

splineTypeItems = [
    ("BEZIER", "Bezier", "Each control point has two handles"),
    ("POLY", "Poly", "Linear interpolation between the spline points")]

class mn_CreateSpline(Node, AnimationNode):
    bl_idname = "mn_CreateSpline"
    bl_label = "Create Spline"
    
    splineType = EnumProperty(name = "Spline Type", items = splineTypeItems, update = nodePropertyChanged)
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorListSocket", "Points")
        self.inputs.new("mn_BooleanSocket", "Cyclic").value = False
        self.outputs.new("mn_SplineSocket", "Spline")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "splineType", text = "")
        
    def getInputSocketNames(self):
        return {"Points" : "points",
                "Cyclic" : "cyclic"}

    def getOutputSocketNames(self):
        return {"Spline" : "spline"}

    def execute(self, points, cyclic):
        if self.splineType == "BEZIER": spline = BezierSpline()
        if self.splineType == "POLY": spline = PolySpline()
        spline.appendPoints(points)
        spline.isCyclic = cyclic
        return spline
