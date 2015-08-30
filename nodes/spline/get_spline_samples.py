import bpy
from ... base_types.node import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

class GetSplineSamplesNode(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_GetSplineSamplesNode"
    bl_label = "Get Spline Samples"

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

    def getExecutionCode(self):
        isLinked = self.getLinkedOutputsDict()
        if not (isLinked["positions"] or isLinked["tangents"]): return []

        lines = []
        add = lines.append
        add("spline.update()")
        add("if spline.isEvaluable:")

        if self.parameterType == "UNIFORM":
            if isLinked["positions"]: add("    positions = spline.getUniformSamples(amount, start, end, self.resolution)")
            if isLinked["tangents"]: add("    tangents = spline.getUniformTangentSamples(amount, start, end, self.resolution)")
        elif self.parameterType == "RESOLUTION":
            if isLinked["positions"]: add("    positions = spline.getSamples(amount, start, end)")
            if isLinked["tangents"]: add("    tangents = spline.getTangentSamples(amount, start, end)")

        add("else: positions, tangents = [], []")

        return lines
