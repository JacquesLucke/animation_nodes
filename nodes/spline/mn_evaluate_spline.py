import bpy
from bpy.props import *
from bpy.types import Node
from mathutils import Vector
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

parameterTypeItems = [
    ("RESOLUTION", "Resolution", ""),
    ("LENGTH", "Length", "")]

class mn_EvaluateSpline(Node, AnimationNode):
    bl_idname = "mn_EvaluateSpline"
    bl_label = "Evaluate Spline"
    
    parameterType = EnumProperty(name = "Parameter Type", default = "LENGTH", items = parameterTypeItems)
    resolution = IntProperty(name = "Resolution", default = 100, min = 2, description = "Increase to have a more accurate evaluation if the type is set to Length")

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_FloatSocket", "Parameter").number = 1.0
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Tangent")
        self.outputs.new("mn_FloatSocket", "Length")
        allowCompiling()
        
    def draw_buttons(self, context, layout):
        layout.prop(self, "parameterType", text = "")
        
    def draw_buttons_ext(self, context, layout):
        col = layout.column()
        col.active = self.parameterType == "LENGTH"
        col.prop(self, "resolution")

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Parameter" : "parameter"}

    def getOutputSocketNames(self):
        return {"Location" : "location",
                "Tangent" : "tangent",
                "Length" : "length"}

    def execute(self, spline, parameter):
        spline.update()
        if spline.isEvaluable:
            if self.parameterType == "LENGTH":
                spline.ensureUniformConverter(self.resolution)
                parameter = spline.toUniformParameter(parameter)
            return spline.evaluate(parameter), spline.evaluateTangent(parameter), spline.getLength()
        else:
            return Vector((0, 0, 0)), Vector((0, 0, 0)), 0.0
