import bpy
from ... base_types.node import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

class GetSplineLength(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_GetSplineLength"
    bl_label = "Get Spline Length"

    inputNames = { "Spline" : "spline",
                   "Start" : "start",
                   "End" : "end" }

    outputNames = { "Length" : "length" }

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline").showName = False
        socket = self.inputs.new("an_FloatSocket", "Start")
        socket.setMinMax(0, 100000)
        socket = self.inputs.new("an_FloatSocket", "End")
        socket.setMinMax(0, 100000)
        socket.value = 1.0
        self.outputs.new("an_FloatSocket", "Length")

    def draw_buttons(self, context, layout):
        layout.prop(self, "parameterType", text = "")

    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")

    def execute(self, spline, start, end):
        spline.update()
        if spline.isEvaluable:
            if start == 0 and end == 1:
                # to get a more exact result on polysplines currently
                return spline.getLength(self.resolution)

            if self.parameterType == "UNIFORM":
                spline.ensureUniformConverter(self.resolution)
                start = spline.toUniformParameter(start)
                end = spline.toUniformParameter(end)
            return spline.getPartialLength(self.resolution, start, end)
        return 0.0
