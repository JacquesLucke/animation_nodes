import bpy
from ... base_types.node import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

class GetSplineSamples(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "mn_GetSplineSamples"
    bl_label = "Get Spline Samples"
    outputUseParameterName = "usedOutputs"

    inputNames = { "Spline" : "spline",
                   "Amount" : "amount",
                   "Start" : "start",
                   "End" : "end" }

    outputNames = { "Positions" : "positions",
                    "Tangents" : "tangents" }

    def create(self):
        self.inputs.new("mn_SplineSocket", "Spline")
        self.inputs.new("mn_IntegerSocket", "Amount").value = 50
        socket = self.inputs.new("mn_FloatSocket", "Start")
        socket.value = 0.0
        socket.setMinMax(0.0, 1.0)
        socket = self.inputs.new("mn_FloatSocket", "End")
        socket.value = 1.0
        socket.setMinMax(0.0, 1.0)
        self.outputs.new("mn_VectorListSocket", "Positions")
        self.outputs.new("mn_VectorListSocket", "Tangents")

    def draw_buttons(self, context, layout):
        layout.prop(self, "parameterType", text = "")

    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")

    def execute(self, usedOutputs, spline, amount, start, end):
        spline.update()
        positions = []
        tangents = []
        if spline.isEvaluable:
            if usedOutputs["Positions"]:
                if self.parameterType == "UNIFORM": positions = spline.getUniformSamples(amount, start = start, end = end, resolution = self.resolution)
                else: positions = spline.getSamples(amount, start = start, end = end)
            if usedOutputs["Tangents"]:
                if self.parameterType == "UNIFORM": tangents = spline.getUniformTangentSamples(amount, start = start, end = end, resolution = self.resolution)
                else: tangents = spline.getTangentSamples(amount, start = start, end = end)
        return positions, tangents
