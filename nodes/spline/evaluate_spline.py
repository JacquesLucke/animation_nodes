import bpy
from bpy.props import *
from mathutils import Vector
from ... base_types.node import AnimationNode
from . spline_evaluation_base import SplineEvaluationBase

class EvaluateSplineNode(bpy.types.Node, AnimationNode, SplineEvaluationBase):
    bl_idname = "an_EvaluateSplineNode"
    bl_label = "Evaluate Spline"

    def create(self):
        self.inputs.new("an_SplineSocket", "Spline", "spline").defaultDrawType = "PROPERTY_ONLY"
        self.inputs.new("an_FloatSocket", "Parameter", "parameter").value = 0.0
        self.outputs.new("an_VectorSocket", "Location", "location")
        self.outputs.new("an_VectorSocket", "Tangent", "tangent")

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
