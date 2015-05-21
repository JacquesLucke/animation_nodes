import bpy
from bpy.types import Node
from ... mn_node_base import AnimationNode
from ... mn_execution import nodePropertyChanged, allowCompiling, forbidCompiling
from ... data_structures.curve import *

class mn_SplineEvaluator(Node, AnimationNode):
    bl_idname = "mn_SplineEvaluator"
    bl_label = "Spline Evaluator"

    def init(self, context):
        forbidCompiling()
        self.inputs.new("mn_SplineSocket", "Spline").showName = False
        self.inputs.new("mn_FloatSocket", "Parameter")
        self.outputs.new("mn_VectorSocket", "Location")
        self.outputs.new("mn_VectorSocket", "Tangent")
        allowCompiling()

    def getInputSocketNames(self):
        return {"Spline" : "spline",
                "Parameter" : "parameter"}

    def getOutputSocketNames(self):
        return {"Location" : "location",
                "Tangent" : "tangent"}

    def execute(self, spline, parameter):
        spline.updateSegments()
        if len(spline.segments) > 0:
            return spline.evaluate(parameter), spline.evaluateTangent(parameter)
        else:
            return Vector((0, 0, 0)), Vector((0, 0, 0))
