import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, nodeTreeChanged, allowCompiling, forbidCompiling

from . import Curves
from . import Surfaces

class mn_CurvePointProjectorNode(Node, AnimationNode):
    bl_idname = "mn_CurvePointProjectorNode"
    bl_label = "Curve Point Projector"
        
    def updateSocketVisibility(self):
        self.inputs["Sampling Resolution"].hide = not (self.mode == "Sampled")
    
    def modeChanged(self, context):
        self.updateSocketVisibility()
        nodeTreeChanged()
    
    modes_items = [ ("Sampled", "Sampled", "Samples a given number of points and outputs the sample/parameter closest to the projecting point"), 
                    ("Analytic", "Analytic", "WIP. Calculates the projection analytically -- eg, by finding the roots of some higher order numpy.Polynomial")]
    mode = bpy.props.EnumProperty(name = "Mode", items = modes_items, default = "Analytic", update = modeChanged)
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "mode")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_VectorSocket", "World Point")
        self.inputs.new("mn_IntegerSocket", "Sampling Resolution").number = Curves.defaultResolutionAnalysis
        self.inputs.new("mn_ObjectSocket", "Curve")
        self.outputs.new("mn_FloatSocket", "Parameter")
        allowCompiling()

    def getInputSocketNames(self):
        return {"World Point" : "point",
                "Sampling Resolution" : "samplingResolution",
                "Curve" : "curve"}

    def getOutputSocketNames(self):
        return {"Parameter" : "parameter"}

    def canExecute(self, point, samplingResolution, curve):
        if self.mode == "Sampled":
            if samplingResolution < 2: return False
        if not Curves.IsBezierCurve(curve): return False

        return True

    def execute(self, point, samplingResolution, curve):
        rvParameter = Curves.defaultParameter
        if not self.canExecute(point, samplingResolution, curve):
            return rvParameter

        try:
            curveCurve = Curves.Curve(curve)
            if self.mode == "Sampled":
                rvParameter = curveCurve.CalcProjection(point, samplingResolution)
                return rvParameter
            if self.mode == "Analytic":
                rvSplineIndex, rvSplineParameter, rvDistance2 = curveCurve.CalcProjectionByPoly5(point)
                rvParameter = curveCurve.CalcParameter(rvSplineIndex, rvSplineParameter)
        except: pass

        return rvParameter
