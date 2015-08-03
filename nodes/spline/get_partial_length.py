import bpy
from ... base_types.node import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from . spline_parameter_evaluate_node_base import SplineParameterEvaluateNodeBase

class mn_GetSplineLength(bpy.types.Node, AnimationNode, SplineParameterEvaluateNodeBase):
    bl_idname = "mn_GetSplineLength"
    bl_label = "Get Spline Length"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        socket = self.inputs.new("mn_FloatSocket", "Start")
        socket.setMinMax(0, 100000)
        socket = self.inputs.new("mn_FloatSocket", "End")
        socket.setMinMax(0, 100000)
        socket.value = 1.0
        self.outputs.new("mn_FloatSocket", "Length")
        allowCompiling()

    def draw_buttons(self, context, layout):
        layout.prop(self, "parameterType", text = "")

    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.active = self.parameterType == "UNIFORM"
        col.prop(self, "resolution")

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Start" : "start",
                "End" : "end"}

    def getOutputSocketNames(self):
        return {"Length" : "length"}

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
