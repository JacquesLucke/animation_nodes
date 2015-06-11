import bpy
from bpy.types import Node
from bpy.props import *
from . mn_spline_parameter_evaluate_node_base import SplineParameterEvaluateNodeBase
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.splines.bezier_spline import BezierSpline
from ... data_structures.splines.poly_spline import PolySpline

class mn_GetSplineSamples(Node, AnimationNode, SplineParameterEvaluateNodeBase):
    bl_idname = "mn_GetSplineSamples"
    bl_label = "Get Spline Samples"
    outputUseParameterName = "useOutput"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline")
        self.inputs.new("mn_IntegerSocket", "Amount").number = 50
        socket = self.inputs.new("mn_FloatSocket", "Start")
        socket.number = 0.0
        socket.setMinMax(0.0, 1.0)
        socket = self.inputs.new("mn_FloatSocket", "End")
        socket.number = 1.0
        socket.setMinMax(0.0, 1.0)
        self.outputs.new("mn_VectorListSocket", "Positions")
        self.outputs.new("mn_VectorListSocket", "Tangents")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "parameterType", text = "")
        
    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")
        
    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Amount" : "amount",
                "Start" : "start",
                "End" : "end"}

    def getOutputSocketNames(self):
        return {"Positions" : "positions",
                "Tangents" : "tangents"}

    def execute(self, useOutput, spline, amount, start, end):
        spline.update()
        positions = []
        tangents = []
        if spline.isEvaluable:
            if useOutput["Positions"]:
                if self.parameterType == "UNIFORM": positions = spline.getUniformSamples(amount, start = start, end = end, resolution = self.resolution)
                else: positions = spline.getSamples(amount, start = start, end = end)
            if useOutput["Tangents"]:
                if self.parameterType == "UNIFORM": tangents = spline.getUniformTangentSamples(amount, start = start, end = end, resolution = self.resolution)
                else: tangents = spline.getTangentSamples(amount, start = start, end = end)
        return positions, tangents
