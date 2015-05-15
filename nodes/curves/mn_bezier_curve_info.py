import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_BezierCurveInfo(Node, AnimationNode):
    bl_idname = "mn_BezierCurveInfo"
    bl_label = "Bezier Curve Info"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierCurveSocket", "Curve")
        self.outputs.new("mn_BezierSplineListSocket", "Splines")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Curve" : "curve"}

    def getOutputSocketNames(self):
        return {"Splines" : "splines"}

    def execute(self, curve):
        return curve.splines
