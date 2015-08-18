import bpy
from ... base_types.node import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

class TrimSpline(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_TrimSpline"
    bl_label = "Trim Spline"

    inputNames = { "Spline" : "spline",
                   "Start" : "start",
                   "End" : "end" }

    outputNames = { "Spline" : "spline" }

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline").showName = False
        self.inputs.new("an_FloatSocket", "Start").value = 0.0
        self.inputs.new("an_FloatSocket", "End").value = 1.0
        self.outputs.new("an_SplineSocket", "Spline")
        
    def draw(self, layout):
        layout.prop(self, "parameterType", text = "")

    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")

    def execute(self, spline, start, end):
        spline.update()
        if spline.isEvaluable and self.parameterType == "UNIFORM":
            spline.ensureUniformConverter(self.resolution)
            start = spline.toUniformParameter(start)
            end = spline.toUniformParameter(end)
        return spline.getTrimmedVersion(start, end)
