import bpy
from ... base_types.node import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

class GetSplineSamples(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_GetSplineSamples"
    bl_label = "Get Spline Samples"
    outputUseParameterName = "usedOutputs"

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline", "spline")
        self.inputs.new("an_IntegerSocket", "Amount", "amount").value = 50
        socket = self.inputs.new("an_FloatSocket", "Start", "start")
        socket.value = 0.0
        socket.setMinMax(0.0, 1.0)
        socket = self.inputs.new("an_FloatSocket", "End", "end")
        socket.value = 1.0
        socket.setMinMax(0.0, 1.0)
        self.outputs.new("an_VectorListSocket", "Positions", "positions")
        self.outputs.new("an_VectorListSocket", "Tangents", "tangents")

    def draw(self, layout):
        layout.prop(self, "parameterType", text = "")

    def drawAdvanced(self, layout):
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
