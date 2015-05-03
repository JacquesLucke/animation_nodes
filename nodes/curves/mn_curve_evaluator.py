import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from mathutils import *

from . import Curves
from . import Surfaces

class mn_CurveEvaluatorNode(Node, AnimationNode):
    bl_idname = "mn_CurveEvaluatorNode"
    bl_label = "Curve Evaluator"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Parameter").number = 0.5
        self.inputs.new("mn_ObjectSocket", "Curve")
        self.outputs.new("mn_VectorSocket", "Local Point")
        self.outputs.new("mn_VectorSocket", "World Point")
        self.outputs.new("mn_VectorSocket", "Local Derivative")
        self.outputs.new("mn_VectorSocket", "World Derivative")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Parameter" : "parameter",
                "Curve" : "curve"}

    def getOutputSocketNames(self):
        return {"Local Point" : "point",
                "World Point" : "pointWorld",
                "Local Derivative" : "derivative",
                "World Derivative" : "derivativeWorld"}

    def canExecute(self, parameter, curve):
        if not Curves.IsBezierCurve(curve): return False

        return True

    def execute(self, parameter, curve):
        point = Vector.Fill(3, 0.0)
        pointWorld = Vector.Fill(3, 0.0)
        derivative = Vector.Fill(3, 0.0)
        derivativeWorld = Vector.Fill(3, 0.0)
        if not self.canExecute(parameter, curve):
            return point, pointWorld, derivative, derivativeWorld

        if parameter < 0.0: parameter = 0.0
        if parameter > 1.0: parameter = 1.0

        try:
            curveCurve = Curves.Curve(curve)
            point = curveCurve.CalcPoint(parameter)
            pointWorld = curveCurve.CalcPointWorld(parameter)
            derivative = curveCurve.CalcDerivative(parameter)
            derivativeWorld = curveCurve.CalcDerivativeWorld(parameter)
        except: pass

        return point, pointWorld, derivative, derivativeWorld
