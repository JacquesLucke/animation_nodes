import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_BezierSplineInfo(Node, AnimationNode):
    bl_idname = "mn_BezierSplineInfo"
    bl_label = "Bezier Spline Info"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_BezierSplineSocket", "Spline")
        self.outputs.new("mn_BezierPointListSocket", "Points")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Spline" : "spline"}

    def getOutputSocketNames(self):
        return {"Points" : "points"}

    def execute(self, spline):
        return spline.points
