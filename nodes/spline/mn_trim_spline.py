import bpy
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from . mn_spline_parameter_evaluate_node_base import SplineParameterEvaluateNodeBase

class mn_TrimSpline(bpy.types.Node, AnimationNode, SplineParameterEvaluateNodeBase):
    bl_idname = "mn_TrimSpline"
    bl_label = "Trim Spline"
    
    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_FloatSocket", "Start").number = 0.0
        self.inputs.new("mn_FloatSocket", "End").number = 1.0
        self.outputs.new("mn_SplineSocket", "Spline")
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
        return {"Spline" : "spline"}

    def execute(self, spline, start, end):
        spline.update()
        if spline.isEvaluable and self.parameterType == "UNIFORM":
            spline.ensureUniformConverter(self.resolution)
            start = spline.toUniformParameter(start)
            end = spline.toUniformParameter(end)
        return spline.getTrimmedVersion(start, end)
