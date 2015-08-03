import bpy
from bpy.props import *
from mathutils import Vector
from . spline_parameter_evaluate_node_base import SplineParameterEvaluateNodeBase
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_EvaluateSpline(bpy.types.Node, AnimationNode, SplineParameterEvaluateNodeBase):
    bl_idname = "mn_EvaluateSpline"
    bl_label = "Evaluate Spline"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_FloatSocket", "Parameter").value = 0.0
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Tangent")
        allowCompiling()

    def draw_buttons(self, context, layout):
        layout.prop(self, "parameterType", text = "")

    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Parameter" : "parameter"}

    def getOutputSocketNames(self):
        return {"Location" : "location",
                "Tangent" : "tangent"}

    def execute(self, spline, parameter):
        spline.update()
        if spline.isEvaluable:
            if self.parameterType == "UNIFORM":
                spline.ensureUniformConverter(self.resolution)
                parameter = spline.toUniformParameter(parameter)
            return spline.evaluate(parameter), spline.evaluateTangent(parameter)
        else:
            return Vector((0, 0, 0)), Vector((0, 0, 0))
