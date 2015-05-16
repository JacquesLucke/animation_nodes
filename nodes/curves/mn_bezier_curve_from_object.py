import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_BezierCurveFromObject(Node, AnimationNode):
    bl_idname = "mn_BezierCurveFromObject"
    bl_label = "Bezier Curve from Object"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_ObjectSocket", "Object").showName = False
        self.outputs.new("mn_BezierCurveSocket", "Bezier Curve")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Object" : "object"}

    def getOutputSocketNames(self):
        return {"Bezier Curve" : "bezierCurve"}

    def execute(self, object):
        if getattr(object, "type", "") != "CURVE":
            return BezierCurve()
        return BezierCurve.fromBlenderCurveData(object.data)
