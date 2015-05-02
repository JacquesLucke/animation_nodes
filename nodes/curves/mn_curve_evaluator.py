import bpy
from bpy.types import Node
from animation_nodes.mn_node_base import AnimationNode
from animation_nodes.mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

from mathutils import *

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
        
    def canExecute(self, parameter, curve):
        if parameter is None: return False
        # do we not execute when par < 0 or par > 1?
        
        if curve is None: return False
        if not Curves.IsBezierCurve(curve): return False
        
        return True
        
    def execute(self, parameter, curve):
        point = Vector.Fill(3, 0.0)
        pointWorld = Vector.Fill(3, 0.0)
        derivative = Vector.Fill(3, 0.0)
        derivativeWorld = Vector.Fill(3, 0.0)
        if not self.canExecute(parameter, curve):
            return point, pointWorld, derivative, derivativeWorld
        
        # is this ok?
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
   
