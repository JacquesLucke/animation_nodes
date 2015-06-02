import bpy
from bpy.types import Node
from mathutils import Vector
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling

class mn_EvaluateSpline(Node, AnimationNode):
    bl_idname = "mn_EvaluateSpline"
    bl_label = "Evaluate Spline"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_FloatSocket", "Parameter").number = 1.0
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Tangent")
        self.outputs.new("mn_FloatSocket", "Length")
        allowCompiling()

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
            return spline.evaluate(parameter), spline.evaluateTangent(parameter), spline.getLength()
        else:
            return Vector((0, 0, 0)), Vector((0, 0, 0)), 0.0
