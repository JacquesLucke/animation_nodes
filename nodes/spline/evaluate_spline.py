import bpy
from bpy.props import *
from mathutils import Vector
from ... base_types.node import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

class EvaluateSpline(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_EvaluateSpline"
    bl_label = "Evaluate Spline"

    inputNames = { "Spline" : "spline",
                   "Parameter" : "parameter" }

    outputNames = { "Location" : "location",
                    "Tangent" : "tangent" }

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline").showName = False
        self.inputs.new("an_FloatSocket", "Parameter").value = 0.0
        self.outputs.new("an_VectorSocket", "Location")
        self.outputs.new("an_VectorSocket", "Tangent")

    def draw(self, layout):
        layout.prop(self, "parameterType", text = "")

    def drawAdvanced(self, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")

    def execute(self, spline, parameter):
        spline.update()
        if spline.isEvaluable:
            if self.parameterType == "UNIFORM":
                spline.ensureUniformConverter(self.resolution)
                parameter = spline.toUniformParameter(parameter)
            return spline.evaluate(parameter), spline.evaluateTangent(parameter)
        else:
            return Vector((0, 0, 0)), Vector((0, 0, 0))
