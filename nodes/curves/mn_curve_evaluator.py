import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurveEvaluatorNode(Node, AnimationNode):
    bl_idname = "mn_CurveEvaluatorNode"
    bl_label = "Evaluator Curve"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_FloatSocket", "Parameter").showName = True
        self.inputs.new("mn_ObjectSocket", "Curve").showName = True
        self.outputs.new("mn_VectorSocket", "Point")
        self.outputs.new("mn_VectorSocket", "PointWorld")
        self.outputs.new("mn_VectorSocket", "Derivative")
        self.outputs.new("mn_VectorSocket", "DerivativeWorld")
        allowCompiling()
        
    def getInputSocketNames(self):
        return {"Parameter" : "parameter",
                "Curve" : "curve"}
        
    def getOutputSocketNames(self):
        return {"Point" : "point",
                "PointWorld" : "pointWorld",
                "Derivative" : "derivative",
                "DerivativeWorld" : "derivativeWorld"}
        
    def execute(self, parameter, curve):
        curveCurve = Curves.Curve(curve)
        
        if parameter < 0.0: parameter = 0.0
        if parameter > 1.0: parameter = 1.0

        point = curveCurve.CalcPoint(parameter)
        pointWorld = curveCurve.CalcPointWorld(parameter)
        derivative = curveCurve.CalcDerivative(parameter)
        derivativeWorld = curveCurve.CalcDerivativeWorld(parameter)
        
        return point, pointWorld, derivative, derivativeWorld
   
