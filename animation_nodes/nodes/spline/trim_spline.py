import bpy
from ... base_types import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

class TrimSplineNode(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_TrimSplineNode"
    bl_label = "Trim Spline"

    def create(self):
        self.newInput("Spline", "Spline", "spline", defaultDrawType = "PROPERTY_ONLY")
        self.newInput("Float", "Start", "start", value = 0.0).setRange(0, 1)
        self.newInput("Float", "End", "end", value = 1.0).setRange(0, 1)
        self.newOutput("Spline", "Spline", "trimmedSpline")

    def draw(self, layout):
        layout.prop(self, "parameterType", text = "")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")

    def execute(self, spline, start, end):
        if not spline.isEvaluable():
            return spline.copy()

        start = min(max(start, 0.0), 1.0)
        end = min(max(end, 0.0), 1.0)

        if self.parameterType == "UNIFORM":
            spline.ensureUniformConverter(self.resolution)
            start = spline.toUniformParameter(start)
            end = spline.toUniformParameter(end)
        return spline.getTrimmedCopy(start, end)
